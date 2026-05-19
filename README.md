
Copyright (C), Hiori Kino, 2017-2026

Apache License Version 2.0（「本ライセンス」）に基づいてライセンスされます。あなたがこのファイルを使用するためには、本ライセンスに従わなければなりません。本ライセンスのコピーは下記の場所から入手できます。

http://www.apache.org/licenses/LICENSE-2.0

# 重要：以下で不明点はLLMに尋ねてください。
Python環境はインターネット上に例が多くあり、回答はほぼ正確です。

# 本レポジトリについて
本レポジトリは各自のPCにPython環境をインストールして使用することを想定していますが、
独自にPython3環境を構築して様々なライブラリをinstallしたを構築しても問題ありません。


# Python環境の構築

本スクリプトはWindows11上でVirtualBox上のubuntu 20.04.4, Miniforge-x86_64版で動作確認をしています。

## Anaconda

condaコマンドでパッケージ管理をする主要なAnaconda系ディストリビューションには以下があります。

* **Anaconda**：Pythonと科学計算用ライブラリが最初から多数入った「全部入り」ディストリビューション。そのため追加パッケージインストールにかなり時間がかかることがある。初心者向けだが、商用利用には制限あり。
* **Miniforge**：conda-forgeコミュニティ提供の完全オープン版。商用利用も含めて無料で、最初から`conda-forge`チャンネルを使用。

### 最近のAnacondaのライセンス

Anaconda Distributionは完全に無料ではありません。
2025年10月15日現在、以下の利用規約ページに詳細が記載されています：

https://www.anaconda.com/legal/terms/terms-of-service

該当箇所は “When Your Use is Free.” の節です。
各自の所属、立場（大学・研究機関・企業など）が無料利用の条件に該当するかを確認してください。

補足：
標準でインストールされるPython本体だけでなく、Anaconda Repository上で提供されている標準的なPythonパッケージ群も有用です。

### Anacondaのインストール

Anaconda(64 bit)を用いる場合は以下からダウンロードできます。

https://www.anaconda.com/download


## 無料環境を利用したい場合

無料で環境を構築する場合は、ある程度のPython環境構築の知識が必要です。
ここでは詳細な手順の説明は省略します。  

### Anaconda系ディストリビューションを使う場合

無料で利用できるAnaconda代替として「Miniforge」を推奨します。

🔗 https://github.com/conda-forge/miniforge

Miniforge は、初期状態で conda-forgeチャンネル（オープンソースリポジトリ） のみを参照するため、
商用・教育・個人利用を問わず 完全に無料 で使用できます。
condaコマンドを用いて追加packageをインストールすることで、Miniconda/Anacondaとほぼ同等の環境構築が可能です。

## 追加インストール

Anacondaはcondaを用いて追加パッケージをインストールできます。

### 重要事項

** scikit-learnのクラス関数が大きく変更されています。
version 1.8.0にて動作確認しています。**

### pymatgen

以下を参照

https://pymatgen.org/installation.html

condaを用いる場合のinstall法が書いてあります。


### pytorch

以下を参照

https://pytorch.org/get-started/locally/


### 他のpackage

各スクリプトに必要パッケージが記載してあります。

## jupyter labの動かし方

以下に説明があります。

https://www.youtube.com/watch?v=WIw_xR6zFjs

## 大規模言語モデル

各人が大規模言語モデルを利用可能にしてください。無料版で十分です。

## 大規模言語モデル例

- OpenAI ChatGPT

- Microsoft copilot

- ANTHROP\C Claude

- Google Gemini

など

-----

# 参考文献

- 「Orange Data Miningではじめるマテリアルズインフォマティクス」木野 日織/ダム，ヒョウ・チ
- 「改訂版Pythonではじめるマテリアルズインフォマティクス-ChatGPTを活用しよう」木野 日織/ダム，ヒョウ・チ

