
Copyright (C), Hiori Kino, 2017-2023 

Apache License Version 2.0（「本ライセンス」）に基づいてライセンスされます。あなたがこのファイルを使用するためには、本ライセンスに従わなければなりません。本ライセンスのコピーは下記の場所から入手できます。

http://www.apache.org/licenses/LICENSE-2.0



# Python環境の構築

本スクリプトはubuntu 22.04.3, Anaconda 2023-09 Linux-x86_64版で動作確認をしています。


各自のPCにPython環境をインストールして使用することを想定しています。
独自に様々なライブラリをinstallしたPython3環境を構築しても問題ありません。

# 最近のAnacondaのライセンス

https://legal.anaconda.com/policies/en/?name=terms-of-service

FREE - For Non-Commercial Personal, Educational, Open Source, and Small Business Use
とあり、教育機関の学生または職員が教育活動に関連して使用する場合は無償で利用できるはずです。
しかし、変更される場合がありますので、Anaconda 2023-09以降の版を利用する場合はご確認ください。


## Anacondaのインストール

Anaconda(64 bit)を用い場合は以下からダウンロードできます。

https://www.anaconda.com/download

そして、ダウンロードしたファイルをインストールしてください。


## 追加インストール

Anacondaはcondaを用いて追加パッケージをインストールできますが、
以下は本授業で動作させる目的のため、簡単にインストールできるpipを用いたインストール法を示します。

### threadpoolctl

Anaconda 2023-09のままではkmeansが動きません。threadpoolctlのupdateを行ってください。
```
pip install -U threadpoolctl>=3.2.0
```

ref.
https://github.com/scikit-learn/scikit-learn/issues/27391


### pymatgen

```
pip install pymatgen
```

ref. https://pymatgen.org/installation.html
はMiniconda(Anacondaとは違う）を用いる場合のinstall法が書いてありますがAnacondaの場合も参考になります。

### progressbar2

```
pip install progressbar2
```

### mlxtend
```
pip install mlxtend
```
ref. https://rasbt.github.io/mlxtend/installation/

## jupyter labの動かし方

以下に説明があります。

https://www.youtube.com/watch?v=WIw_xR6zFjs

## 大規模言語モデル

各人が大規模言語モデルを利用可能にしてください。無料版で十分です。

## 大規模言語モデル例

- OpenAI ChatGPT: https://openai.com/chatgpt

ChatGPTなどのOpenAIのサービスで入力を学習させないためにはこちらから申請してください。
OpenAI Privacy Request Portal https://privacy.openai.com/policies

- Microsoft copilot: https://copilot.microsoft.com/

- Google Bard: https://bard.google.com/

- ANTHROP\C Claude https://www.anthropic.com/index/claude-2-1


-----

# 参考文献

- 「Orange Data Miningではじめるマテリアルズインフォマティクス」木野 日織/ダム，ヒョウ・チ
- 「Pythonではじめるマテリアルズインフォマティクス」木野 日織/ダム，ヒョウ・チ
- https://bitbucket.org/kino_h/orange_mi_seminar_2023/src/main/ スライド、youtune動画へのリンクあり。
- https://bitbucket.org/kino_h/python_mi_seminar_2023/src/master/ スライド、youtub動画へのリンクあり。

