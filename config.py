import argparse


def get_arguments():

    parser = argparse.ArgumentParser(
        description='PyTorch implementation of the paper: Long-tail Learning via Logit Adjustment')
    parser.add_argument('--dataset', default="cifar10-lt", type=str, help='Dataset to use.',
                        choices=["cifar10", "cifar100", "cifar10-lt", "cifar100-lt","imagenet"])
    parser.add_argument('--data_home', default="data", type=str,
                        help='Directory where data files are stored.')
    parser.add_argument('--num_workers', default=2, type=int, metavar='N',
                        help='number of workers at dataloader')
    parser.add_argument('--batch_size', default=128, type=int, help='mini-batch size (default: 128)')
    parser.add_argument('--lr', default=0.1, type=float, help='initial learning rate')
    parser.add_argument('--momentum', default=0.9, type=float, help='momentum')
    parser.add_argument('--weight-decay', default=1e-4, type=float, help='weight decay (default: 1e-4)')
    parser.add_argument('--log_val', help='compute val acc', type=int, default=10)
    parser.add_argument('--logit_adj_post', help='adjust logits post hoc', type=int, default=0, choices=[0, 1])
    parser.add_argument('--tro_post_range', help='check diffrent val of tro in post hoc', type=list,
                        default=[0.25, 0.5, 0.75, 1, 1.5, 2])
    parser.add_argument('--logit_adj_train', help='adjust logits in trainingc', type=int, default=0, choices=[0, 1])
    parser.add_argument('--br', help='enable batch reweighting', type=int, default=0, choices=[0, 1])
    parser.add_argument('--rc', help='representation correction', type=int, default=0, choices=[0, 1])
    parser.add_argument('--gamma', help='threshold for gradient similarity', type=float, default=0.7)
    parser.add_argument('--tro_train', default=1.0, type=float, help='tro for logit adj train')
    parser.add_argument('--update_gap', default=50, type=int, help='updating weights gap')
    parser.add_argument('--measure', default=0, type=int, help='0 for gradient, 1 for embedding and 2 for gradient+embedding',choices=[0,1,2])
    parser.add_argument('--temp', default=1, type=float, help='tempreturen in softmax')
    parser.add_argument('--norm', default=1, type=int, help='0 for not normalize 1 for normalize', choices=[0,1])
    parser.add_argument('--temp_decay', default=0, type=float, help='tempreturen decay in softmax',choices = [0,1])
    parser.add_argument('--off_diag', default=0, type=float, help='minus off_diag*identity matrix')
    parser.add_argument('--attn', default=0, type=int, help='Attention?', choices=[0,1])
    parser.add_argument('--save_dir', default='image', type=str, help='dir to save image')
    parser.add_argument('--wo', default=0, type=int, help='weighting option. 0 for softmax, 1 for inverse', choices=[0,1])
    parser.add_argument('--eps', default=0.5, type=float, help='small value to avoid divided by 0')
    parser.add_argument('--cumulative', default=0, type=int, help='whether to cumulate the score', choices =[0,1])

    




    return parser
