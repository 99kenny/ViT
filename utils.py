import torch
from tqdm import tqdm
import requests

def download_pretrained(path:str, model_name:str="vit_B_16"):
    if model_name == "vit_B_16":
        url = "https://github.com/lukemelas/PyTorch-Pretrained-ViT/releases/download/0.0.2/B_16_imagenet1k.pth"
        print("start downloading {}...".format(model_name))
        r = requests.get(url, allow_redirects=True)
        open('{}/ViT_B_16.pth'.format(path), 'wb').write(r.content)
    
    return '{}/ViT_B_16.pth'.format(path)
    

def accuracy(output, y):
    pred = output.topk(k=1).indices
    pred = torch.reshape(pred, (-1,))
    guess = pred - y
    acc = len((guess == 0).nonzero()) / len(y)
    return acc

def train(train_loader, model, criterion, optimizer, epoch, writer):
    losses = 0.
    accs = 0.
    # train mode
    model.train()
    # one epoch
    for i, (input, target) in tqdm(enumerate(train_loader),desc="Epoch:{} Train".format(epoch),total=len(train_loader)):
        target = target.cuda()
        input = input.cuda()

        #forward
        output = model(input)
        loss = criterion(output, target)

        # compute grad
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        output = output.float()
        losses += loss.float().item()
        accs += accuracy(output.data, target)

    losses /= len(train_loader)
    accs /= len(train_loader)
    print("Epoch:{} trian_loss:{}".format(epoch,losses))
    print("Epoch:{} train_acc:{}".format(epoch,accs))
    writer.add_scalar("Loss/train", losses, epoch)
    writer.add_scalar("Accuracy/train", accs, epoch)

    return accs
def validate(val_loader, model, criterion, epoch, writer):
    losses = 0.
    accs = 0.

    # evaluation mode
    model.eval()

    with torch.no_grad():
        for i, (input, target) in tqdm(enumerate(val_loader),desc="Epoch:{} Val:".format(epoch),total=len(val_loader)):
            target = target.cuda()
            input = input.cuda()

            # compute output
            output = model(input)
            loss = criterion(output, target)
            output = output.float()
            loss = loss.float().item()

            # measure accuracy and record loss
            accs += accuracy(output.data, target)
            losses += loss

        losses /= len(val_loader)
        accs /= len(val_loader)
        print("Epoch:{} val_loss:{}".format(epoch,losses))
        print("Epoch:{} val_acc:{}".format(epoch,accs))
        writer.add_scalar("Loss/val", losses, epoch)
        writer.add_scalar("Accuracy/val", accs, epoch)

    return accs