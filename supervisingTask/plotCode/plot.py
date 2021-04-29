from matplotlib import colors
import matplotlib.pyplot as plt
from convertor import readData

def showPicture(path):
    #get results
    sm0, mem0, sm1, mem1 = readData(path)
    length = int(len(mem0)/2)

    fig = plt.figure(1)

    #ax1 for sm
    ax1 = plt.subplot(1,2,1)
    ax1.axis([0, length, 0, 100])
    x = [i for i in range(length)]
    plt.xlabel('time(s)')
    plt.ylabel('usage\%')
    plt.title('SM of %s'%(path))
    line_sm0, = plt.plot(x, sm0[:length], color='green', lw=0.5)
    line_sm1, = plt.plot(x, sm1[:length], color='red', lw=0.5)
    plt.legend(handles=[line_sm0, line_sm1], labels=['cuda:0', 'cuda:1'], loc='best')

    #ax2 for mem
    ax2 = plt.subplot(1,2,2)
    ax2.axis([0, length, 0, 100])
    x = [i for i in range(length)]
    plt.xlabel('time(s)')
    plt.ylabel('usage\%')
    plt.title('MEM of %s'%(path))
    line_mem0, = plt.plot(x, mem0[:length], color='green', lw=0.5)
    line_mem1, = plt.plot(x, mem1[:length], color='red', lw=0.5)
    plt.legend(handles=[line_mem0, line_mem1], labels=['cuda:0', 'cuda:1'], loc='best')

    plt.show()

if __name__ == '__main__':
    showPicture('vgg11_cifar10_gpu.out')