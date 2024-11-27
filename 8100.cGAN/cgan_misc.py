import matplotlib.pyplot as plt


def show_generated_images(generated_imgs, epoch=None):
    """
    渡された生成画像を表示する関数。

    Parameters:
    - generated_imgs (list or ndarray): 生成された画像のリストまたは配列。
    - epoch (int, optional): エポック数。指定された場合、タイトルにエポック数を追加。

    Returns:
    - None
    """
    fig, axes = plt.subplots(1, 10, figsize=(10, 1))
    for i, img in enumerate(generated_imgs):
        axes[i].imshow(img, cmap='gray')
        axes[i].axis('off')
    if epoch is not None:
        plt.suptitle(f'Epoch {epoch}: Generated Images')
    plt.show()


def plot_losses(losses_d, losses_g):
    """
    DiscriminatorとGeneratorの損失の推移をプロットする関数。

    Parameters:
    - losses_d (list or ndarray): Discriminatorの損失のリストまたは配列。
    - losses_g (list or ndarray): Generatorの損失のリストまたは配列。

    Returns:
    - None
    """
    plt.figure(figsize=(10, 5))
    plt.plot(losses_d, label='Discriminator')
    plt.plot(losses_g, label='Generator')
    plt.yscale('log')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.show()


def show_original_images(X, y, index_from=0):
    """
    元画像を表示する関数。

    Parameters:
    - X (ndarray): 入力画像の配列。
    - y (ndarray): 入力画像に対応するラベルの配列。
    - index_from (int, optional): 表示を開始するインデックス。

    Returns:
    - None
    """
    imgs = X[index_from:index_from+10]
    labels = y[index_from:index_from+10]
    print(f'data from {index_from} to {index_from+9}')
    fig, axes = plt.subplots(1, 10, figsize=(10, 1))
    for i, (img, label) in enumerate(zip(imgs, labels)):
        axes[i].imshow(img.reshape(8, 8), cmap='gray')
        axes[i].axis('off')
        axes[i].set_title(label)
    plt.show()
