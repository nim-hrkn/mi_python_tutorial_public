
import matplotlib.pyplot as plt


def plot_loss_history(loss_history):
    # 損失履歴の表示
    plt.figure()
    plt.plot(range(len(loss_history)), loss_history)
    plt.yscale('log')
    plt.xlabel('Epoch')
    plt.ylabel('Loss (log scale)')
    plt.title('Loss History')
    plt.show()


def show_images(original, noisy, denoised, epoch, nbins=30):
    # 元画像、ノイズ画像、デノイズ画像の表示
    plt.figure(figsize=(15, 5))

    plt.subplot(1, 3, 1)
    plt.imshow(original, cmap='gray')
    plt.title('Original Image')

    plt.subplot(1, 3, 2)
    plt.imshow(noisy, cmap='gray')
    plt.title('Noisy Image')

    plt.subplot(1, 3, 3)
    plt.imshow(denoised, cmap='gray')
    plt.title(f'Denoised Image (Epoch {epoch})')

    plt.show()

    # ヒストグラムの表示
    plt.figure(figsize=(15, 5))

    plt.subplot(1, 3, 1)
    plt.hist(original.ravel(), bins=nbins, range=(0, 1))
    plt.title('Original Image Histogram')

    plt.subplot(1, 3, 2)
    plt.hist(noisy.ravel(), bins=nbins, range=(0, 1))
    plt.title('Noisy Image Histogram')

    plt.subplot(1, 3, 3)
    plt.hist(denoised.ravel(), bins=nbins, range=(0, 1))
    plt.title('Denoised Image Histogram')

    plt.show()


def plot_metric_history(history, title, xlabel, ylabel, log_scale=False):
    plt.figure()
    plt.plot(range(len(history)), history)
    if log_scale:
        plt.yscale('log')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.show()
