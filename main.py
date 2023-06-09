import torch
import torchvision
import torchvision.transforms as transforms
import torch.nn as nn
import torch.optim as optim
import timm
import random
import numpy as np

model_num = 3 # total number of models
total_epoch = 200 # total epoch
# lr = 0.01 # initial learning rate
lr = 0.0001

epochs = []
accs = []

def run():
    for s in range(model_num):
        # fix random seed
        seed_number = s
        random.seed(seed_number)
        np.random.seed(seed_number)
        torch.manual_seed(seed_number)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

        # Check if GPU is available
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(device)

        # Define the data transforms
        transform_train = transforms.Compose([
            transforms.Resize(256),
            transforms.RandomCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
        ])

        transform_test = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
        ])

        # Load the CIFAR-10 dataset
        trainset = torchvision.datasets.CIFAR10(root='./data', train=True, download=True, transform=transform_train)
        trainloader = torch.utils.data.DataLoader(trainset, batch_size=16, shuffle=True, num_workers=16)

        testset = torchvision.datasets.CIFAR10(root='./data', train=False, download=True, transform=transform_test)
        testloader = torch.utils.data.DataLoader(testset, batch_size=16, shuffle=False, num_workers=16)

        # Define the ResNet-18 model with pre-trained weights
        model = timm.create_model('resnet18', pretrained=True, num_classes=10)
        model = model.to(device)  # Move the model to the GPU

        # Define the loss function and optimizer
        criterion = nn.CrossEntropyLoss()
        # optimizer = optim.SGD(model.parameters(), lr=lr, momentum=0.9, weight_decay=1e-4)
        optimizer = optim.Adam(model.parameters(), lr=lr, eps=1e-8)
        # Define the learning rate scheduler
        # scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=30, gamma=0.1)

        def train():
            model.train()
            running_loss = 0.0

            for i, data in enumerate(trainloader, 0):
                inputs, labels = data
                inputs, labels = inputs.to(device), labels.to(device)  # Move the input data to the GPU
                optimizer.zero_grad()
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                running_loss += loss.item()
                if i % 100 == 99:
                    print('[%d, %5d] loss: %.3f' % (epoch + 1, i + 1, running_loss / 100))
                    running_loss = 0.0

        def test():
            model.eval()

            # Test the model
            correct = 0
            total = 0
            with torch.no_grad():
                for data in testloader:
                    images, labels = data
                    images, labels = images.to(device), labels.to(device)  # Move the input data to the GPU
                    outputs = model(images)
                    _, predicted = torch.max(outputs.data, 1)
                    total += labels.size(0)
                    correct += (predicted == labels).sum().item()

            acc = 100 * correct / total
            print('Accuracy of the network on the 10000 test images: %f %%' % (acc))

            return acc


        # Train the model
        best_acc = 0
        PATH = './resnet18_cifar10_%f_%d.pth' % (lr, seed_number)
        for epoch in range(total_epoch):
            train()
            acc = test()
            if acc > best_acc:
                torch.save(model.state_dict(), PATH)
                best_acc = acc
                best_epoch = epoch
            # scheduler.step()
            print(f"now try {s} : the best acc is {best_acc} and its epoch is {best_epoch}")
            print(f"this is Try {s} : epochs is {epochs}, and accs is {accs}")

        print('Finished Training')
        print(f"Try {s} : best accuracy is {best_acc} and its epoch is {best_epoch}")
        epochs.append(best_epoch)
        accs.append(best_acc)
        print(f"this is Try {s} : epochs is {epochs}, and accs is {accs}")
    print(f"epochs is {epochs}, and accs is {accs}")

if __name__ == '__main__' :
    run()
