import torch.nn as nn
import torch.nn.parallel
import torch.backends.cudnn as cudnn
import torch.optim
import torch.utils.data
from model import resnet32
from utils import *
from config import get_arguments
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm

parser = get_arguments()
args = parser.parse_args()

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
args.device = device

exp_loc, model_loc = log_folders(args)
writer = SummaryWriter(log_dir=exp_loc)


def main():
    global args
    # cant do both at same time
    assert (not (args.logit_adj_post and args.logit_adj_train))

    model = torch.nn.DataParallel(resnet32())
    model = model.to(device)

    train_loader, val_loader = get_loaders(args)
    args.logit_adjustments = compute_adjustment(train_loader, args)

    criterion = nn.CrossEntropyLoss().to(device)
    optimizer = torch.optim.SGD(model.parameters(),
                                args.lr,
                                momentum=args.momentum,
                                weight_decay=args.weight_decay)
    lr_scheduler = torch.optim.lr_scheduler.MultiStepLR(optimizer,
                                                        milestones=args.scheduler_steps)

    cudnn.benchmark = True

    if args.evaluate:
        if os.path.isfile(os.path.join(model_loc, "model.th")):
            print("=> loading checkpoint ")
            checkpoint = torch.load(os.path.join(model_loc, "model.th"))
            model.load_state_dict(checkpoint['state_dict'])
            val_loss, val_acc = validate(val_loader, model, criterion)
            results = class_accuracy(val_loader, model, args)
            results["OA"] = val_acc
            print(results)
            hyper_param = log_hyperparameter(args)
            writer.add_hparams(hparam_dict=hyper_param, metric_dict=results)
            writer.close()
        else:
            print("=> no checkpoint found")

        return

    loop = tqdm(range(0, args.epochs), total=args.epochs, leave=False)
    val_loss, val_acc = 0, 0
    for epoch in loop:

        # train for one epoch
        train_loss, train_acc = train(train_loader, model, criterion, optimizer)
        writer.add_scalar("train/acc", train_acc, epoch)
        writer.add_scalar("train/loss", train_loss, epoch)
        lr_scheduler.step()

        # evaluate on validation set
        if (epoch % args.log_val) == 0 or (epoch == (args.epochs - 1)):
            val_loss, val_acc = validate(val_loader, model, criterion)
            writer.add_scalar("val/acc", val_acc, epoch)
            writer.add_scalar("val/loss", val_loss, epoch)

        loop.set_description(f"Epoch [{epoch}/{args.epochs}")
        loop.set_postfix(train_loss=f"{train_loss:.2f}", val_loss=f"{val_loss:.2f}", train_acc=f"{train_acc:.2f}",
                         val_acc=f"{val_acc:.2f}")

    file_name = 'model.th'
    mdel_data = {"state_dict": model.state_dict()}
    torch.save(mdel_data, os.path.join(model_loc, file_name))

    results = class_accuracy(val_loader, model, args)
    results["OA"] = val_acc
    hyper_param = log_hyperparameter(args)
    print(results)
    writer.add_hparams(hparam_dict=hyper_param, metric_dict=results)
    writer.close()


def train(train_loader, model, criterion, optimizer):
    """ Run one train epoch """

    losses = AverageMeter()
    accuracies = AverageMeter()

    # switch to train mode
    model.train()

    for i, (inputs, target) in enumerate(train_loader):
        target = target.to(device)
        input_var = inputs.to(device)
        target_var = target

        # compute output
        output = model(input_var)
        if args.logit_adj_train:
            output = output + args.logit_adjustments
        loss = criterion(output, target_var)

        # compute gradient and do SGD step
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        output = output.float()
        loss = loss.float()
        # measure accuracy and record loss
        acc = accuracy(output.data, target)
        losses.update(loss.item(), inputs.size(0))
        accuracies.update(acc, inputs.size(0))

    return losses.avg, accuracies.avg


def validate(val_loader, model, criterion):
    """ Run evaluation """

    losses = AverageMeter()
    accuracies = AverageMeter()

    # switch to evaluate mode
    model.eval()

    with torch.no_grad():
        for i, (inputs, target) in enumerate(val_loader):
            target = target.to(device)
            input_var = inputs.to(device)
            target_var = target.to(device)

            # compute output
            output = model(input_var)
            if args.logit_adj_post:
                output = output - args.logit_adjustments

            loss = criterion(output, target_var)

            output = output.float()
            loss = loss.float()

            # measure accuracy and record loss
            acc = accuracy(output.data, target)
            losses.update(loss.item(), inputs.size(0))
            accuracies.update(acc, inputs.size(0))

    return losses.avg, accuracies.avg


if __name__ == '__main__':
    main()
