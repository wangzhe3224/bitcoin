---
title: 比特币的技术细节
tags: Bitcoin
---

- [1. 有限域，Finite Field](#1-有限域finite-field)
- [2. 椭圆曲线](#2-椭圆曲线)
  - [点的相加](#点的相加)
- [3. 椭圆曲线密码学](#3-椭圆曲线密码学)
  - [椭圆曲线的标量乘法](#椭圆曲线的标量乘法)
  - [组，Groups](#组groups)
  - [定义比特币的曲线](#定义比特币的曲线)
  - [公钥密码学](#公钥密码学)
  - [签名和验证](#签名和验证)
  - [验证过程](#验证过程)
  - [签名过程](#签名过程)
  - [结论](#结论)
- [4. 序列化](#4-序列化)
  - [SEC](#sec)
  - [DER 签名](#der-签名)
  - [Base58](#base58)
  - [WIF 格式](#wif-格式)
  - [如何操作？](#如何操作)
- [5. 交易, Transaction](#5-交易-transaction)
  - [输入](#输入)
  - [输出](#输出)
  - [UTXO](#utxo)
  - [Locktime](#locktime)
  - [交易费用](#交易费用)
- [6. Script](#6-script)
- [7. 交易创建和验证](#7-交易创建和验证)
- [8. Pay-to-Script Hash](#8-pay-to-script-hash)
- [9. 区块，Blocks](#9-区块blocks)

比特币的核心是椭圆曲线加密技术，而明白这个加密技术，我们需要两个数学知识：有限域 和 椭圆曲线。

1 - 8 章主要针对单个交易，9章开始，进入区块，即多个交易。

## 1. 有限域，Finite Field

有限域听起来很可怕，但是其实他是一种很简单的代数系统，不会比我们初中学过的基础代数更困难。（当然，我不是数学家，我相信有限域可以非常复杂，只不过对于我们理解比特币，一点点粗浅的理解就够了）

有限域的定义：一组有限的数集，支持两个操作 + 和 *，且这两个操作满足：

- 闭合：如果 a 和 b 在有限域，那么 a+b 和 a*b 也在有限集
- 加性同一性：0 存在，且 `a+0=a`
- 乘性同一性：1 存在，且 `a*1=a`
- 加性反身：a 在有限域，则 -a 也在，且有 `a - a = 0`
- 乘性反身：a 在有限域且不是0，则 `a^-1` 也在有限域，且 `a * a^-1 = 1`

数学上，有限集表达成为：$F_p = \{0, 1, ..., p-1\}$，我们称 $F_p$ 是 P 域，即包含了 p 个元素的有限域。注意，有限域不需要定义在数集上。

*注意*：p 为质数的有限域我们更加关心。

让一个整数有限域满足闭合条件，我们需要模算术（Modulo Arithmetic），即 `7 % 3 = 1` 这样的计算。详细定义见 Python 代码 `ecc.py`。

## 2. 椭圆曲线

椭圆曲线定义如下：$y^2 = x^3 + ax + b$

给出一组ab，我们可以根据上述公式判断一个点`(x, y)`是否在该椭圆曲线上。

### 点的相加

椭圆曲线的一个重要特征就是点相加，即两个去曲线上的点相加，结果仍然在曲线上（是不是想到了有限域的闭合属性？）。

当我们画一条直线，与椭圆曲线相交，那么交点只可能是1个、2个、或者3个，2个点的为特殊情况。我们按照下图定义点的加法：

![20220205220423](https://raw.githubusercontent.com/wangzhe3224/pic_repo/master/images/20220205220423.png)

点的加法满足如下特性：

- 同一性，I + A = A
- 交换律，A + B = B + A
- 结合律，A + （B+C） = （A+B）+ C
- 反身性，A + （-A）= I

详细定义见 Python 代码 `ecc.py`。

## 3. 椭圆曲线密码学

正如我们上一小节看到的，椭圆曲线可以定在实数域，当然我们也可以定义在有限域中！只不过他们看起来已经不是曲线或者直线了。

![有限域的椭圆曲线](https://raw.githubusercontent.com/wangzhe3224/pic_repo/master/images/20220205225556.png)

![有限域的直线](https://raw.githubusercontent.com/wangzhe3224/pic_repo/master/images/20220205225619.png)

椭圆曲线点加法也在有限域成立。

### 椭圆曲线的标量乘法

我们知道 `(170, 142) + (170, 142) = 2 . (170, 142)`，而椭圆曲线的标量乘法有一个重要的特性：
难以预测他的位置！

![标量乘法](https://raw.githubusercontent.com/wangzhe3224/pic_repo/master/images/20220205230111.png)

这也被称作*离散对数问题*，也是椭圆曲线密码学的基础之一。

标量乘法的另一个特性是：对一个定不断进行标量乘法，最终会产生一个无限点，I。而这一系列点的被称为一个组，Group

$$\{G, 2G, ..., nG\} where nG = 0$$

椭圆曲线的标量乘法难以求逆，这就是公钥密码学的基础。

比如，我们可以轻松的计算 `20*(47,71)=(47,152)`，但是，如果给出 `?*(47,71)=(47,152)`，想要找到 `?` 计算量就很大。特别是当组的规模很大时，取逆非常困难。这就是非对称加密的核心。

### 组，Groups

我们机已经介绍了两个基本工具：有限域 和 椭圆曲线，以及他们的组合，定义在有限域的椭圆曲线。然后，我们发现了一个有用的概念：组。而椭圆曲线密码学的关键就在于：有限循环组，Finite Cyclic Group。在有限域椭圆曲线上取一个点，我们可以
生成一个有限循环组。

与域不同，组只有一个运算，点加法。点加法具有如下特性：

- 同一性，0 + A = A
- 闭包，aG + bG = (a+b)G
- 可逆，aG 在组里，则 (n-a)也在，$aG + (n-a)G = nG = 0$
- 交换律，aG + bG = bG + aG
- 结合律，aG + (bG + cG) = (aG + bG) + cG

问题：给出一个在 $F_223$ 的曲线： $y^2 = x^3 + 7$，找到组 $(15, 86)$ 的序（Order）？
([代码](./ecc.py))

### 定义比特币的曲线

当组的规模变得的很大时，破解离散对数问题非常挑战。公钥密码学的椭圆曲线定义如下：

- 有参数，ab，$y^2 = x^3 + ax + b$
- 有限域 $F_{p}$，$p$ 是质数
- 选择 $x,y$ 生成点 $G$
- 选择组的序，$G, n$

上述参数都是公开的，比特币使用了一种叫做：`secp256k1` 的参数。

- a = 0, b=7, 因此曲线为 $y^2 = x^3 + 7$
- $p = 2^{256} - s^{32} - 977$
- $G_x = 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798$
- $G_y = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8$
- $n = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141$

这个组有一些值得注意的特点：

- 曲线公式非常简单
- $p$ 非常接近 $2^{256}$，话句话说是一个巨大的有限域，但是每个点的坐标都可以用 256 bit 表达
- $n$ 也非常接近 $2^{256}$，标量乘法也可以用 256 位表达

比特币组 [Code](./ecc.py)

### 公钥密码学

$P = eG$，给出 e 和 G 我们可以轻松计算 P，但是给出 P 和 G，计算 e 非常困难。这就是所谓的非对称方程，也就是我们之前提到的离散对数问题。

我们称 $e$ 为**私钥** (private key)，而 $G$ 点的两个坐标 $(x, y)$。其中，xye都是 256 位整数。$P$ 是公钥。

### 签名和验证

其实我们要做的事情很简单，就是如何证明你知道一个秘密的整数。

签名算法，特别的，椭圆曲线数字签名算法，ECDSA。

$eG = P$，跟上文一样 $e$ 是秘密数字，私钥；$P$ 是公钥

我们的目标是，对于一个随机数字 $k$

$$kG = R$$

这里我们仅仅关心 $R$ 的 x 坐标，$r$。

这时，我们说下面的方程等价于离散对数问题：

$$\mu G + vP = kG$$

其中，$k$ 是随机选择的，$\mu,v \neq 0$，且由签名者选择，$G,P$ 是公开信息。因为 $v \neq 0$,

$$P = ((k-\mu) / v)G$$

如果我们知道 $e$，

$$eG =((k-\mu) / v)G$$

或者 

$$e =((k-\mu) / v)$$

对于给出的 P 和 G，为了满足 $P = eG$，我们有两种方案：

- 知道 $e$
- 破解 $(\mu, v)$

选择 $(\mu, v)$ 我们需要考虑两个因素，一个是 R 的 x 坐标，$r$，另一个是我们签名的信息 $z$，其中 z 需要是一个信息的 Hash，来确保他是 256 位的，比如采用 sha256。

我们有：

$\mu = z/s, v = r/s$

其中，$s = (z+re)/k$

这就是一个基本的签名算法，签名中的两个数是：$r$, $s$。

验证签名非常直接：

$$\mu G + vP,  \mu,v \neq 0$$
$$\mu G + vP = kG = (r, y)$$

### 验证过程

- 给出 $(r,s)$ 作为签名，$z$ 是我们的签名的信息的哈希，$P$ 是签名者的公钥
- 计算 $\mu = z/s, v = r/s$
- 计算 $\mu G + vP = R$
- 如果 R 的 x 坐标等于 $r$，签名就是有效的

### 签名过程

- 给出 $z$，我们知道自己的私钥 $e$，且满足 $eG = P$
- 选择一个随机数 $k$，k 的随机性非常重要，否则私钥就会泄漏
- 计算 R，得到 R 的 x 坐标
- 计算 s，$s = (z + re)/k$，因为 s 包含了 e 所以 k 的随机性很重要
- 得到签名 (r,s)

比特币签名和验证 [Code](./ecc.py)

### 结论

现在我们已经介绍了椭圆曲线密码学，以及如何签名和验证，下一步我们需要通过序列化和反序列化在网络上传输这些信息，在硬盘上存储这些信息。

## 4. 序列化

我们已经有了一些比特币的基本 Class，比如 `PrivateKey`, `S256Point`, `Signature`。我们需要高效在网络和硬盘上传输和存储这些数据。

### SEC

首先，是我们的公钥，`S256Point`，实际上我们需要传输的只有两个 256 位的整数，即坐标 `(x, y)`。

非压缩的压缩方法可以是：

1. 前缀：`0x04`
2. x 坐标，32 byte, big endian
3. y 坐标，32 byte, bit endian

注意，定义在有限域的椭圆曲线上的点 $(x, y)$，当我们知道 $x$ 的值， $y$ 只有两种可能：$y$ 或者 $p-y$，
我们知道 $p$ 是一个素数，所以也是一个奇数，因此如果 y 是奇数，则 p-y 就是偶数。所以，我们只需要序列化 x 和 y 奇偶性即可。

这样，我们用 33 个字节就可以表达公钥 P 了。

### DER 签名

下一步，我们需要序列化签名，实际上就是 $(r, s)$，我们用到的方法是：Distinguished Encoding Rules (DER)。这也是 Satoshi 使用的序列化方法。

### Base58

想要交换比特币，我们需要提供公钥，无论是 Sec 还是压缩 Sec，我们需要 65 或者 33 字节。
但是这样的地址（公钥）非常不易于人类读写，而且容易出错。比特币给出的方案是一个缩减版的 Base64 编码：Base58。
去掉了一些容易混淆的字母，比如 I 和 1，,0 和 o 等等。

真实的比特币地址使用了一种更加短的格式，hash160

1. For mainnet addresses, start with the prefix 0x00, for testnet 0x6f.
2. Take the SEC format (compressed or uncompressed) and do a sha256 operation followed by the ripemd160 hash operation, the combination of which is called a hash160 operation.
3. Combine the prefix from #1 and resulting hash from #2.
4. Do a hash256 of the result from #3 and get the first 4 bytes.
5. Take the combination of #3 and #4 and encode it in Base58.

``` text
* 5002 (use uncompressed SEC on testnet)
* 2020^5^ (use compressed SEC on testnet)
* 0x12345deadbeef (use compressed SEC on mainnet)
# end::exercise5[]
# tag::answer5[]
>>> from ecc import PrivateKey
>>> priv = PrivateKey(5002)
>>> print(priv.point.address(compressed=False, testnet=True))
mmTPbXQFxboEtNRkwfh6K51jvdtHLxGeMA
>>> priv = PrivateKey(2020**5)
>>> print(priv.point.address(compressed=True, testnet=True))
mopVkxp8UhXqRYbCYJsbeE1h1fiF64jcoH
>>> priv = PrivateKey(0x12345deadbeef)
>>> print(priv.point.address(compressed=True, testnet=False))
1F1Pn2y6pDb68E5nYJJeba4TLg2U7B6KF1
```

### WIF 格式

接下来，我们序列化我们的私钥，但是，通常我们不需要序列化私钥，因为我们不想经常暴露他们。。
当然，有些情况我们需要序列化私钥，比如 Paper 钱包传到网上。

Wallet Import Format (WIF).

### 如何操作？

``` text
sec = 123456
priv = PrivateKey(sec)
address = priv.point.address(testnet=True)
```

## 5. 交易, Transaction

Transaction, Tx, 是比特币的核心，主要包括四个部分：

- 版本，Version
- 输入，Inputs
- 输出，Outputs
- 锁，Locktime

![交易的具体信息](https://raw.githubusercontent.com/wangzhe3224/pic_repo/master/images/20220208192319.png)

其中，locktime 被新的闪电网络取代了，因为存在安全隐患。

### 输入

每一笔交易的输入(inputs)都是前一个交易的输出（Output），每一个输入需要包含两个部分：

- 你收到的比特币记录（reference）
- 证明你可以支付这些比特币（ESDSA）

技术上，每一个输入需要：

- 前一笔交易的 ID （32 字节）， hash256 of the previous transaction’s contents.
- 前一笔交易的 Index（4 字节），
- ScriptSig
- Sequence

### 输出

输出中也可以存在多个目标：

- 数量
- ScriptPublicKey

### UTXO

UTXO, unspent transaction output，代表了比特币当前的总供应量，对验证也有帮助。

### Locktime

Locktime 是一个有延迟的交易。如果一笔交易的 Locktime 是 600，那么这笔交易只能在第 601 个区块上验证。

### 交易费用

比特币的共识算法之一是：对于任何非 Coinbase 交易，输入的总和必须大于等于输出的总和，这样可以激励矿工选择费用更高的交易。没有进入区块的交易被称为：mempool transactions。

## 6. Script

一种基于栈的图灵不完备语言。连接前一笔交易 ScriptPubKey 和 当前的 ScriptSig。

## 7. 交易创建和验证

对于一个节点，当它收到一笔交易，他需要验证这笔交易是不是符合比特币协议，这个过程就叫做**验证**：

- 输入没有被消费过(防止 double spending)
- 输入之和大于输出之和
- ScriptSig 可以解锁 ScriptPubKey

The Value Overflow Incident - CVE-2010-5139

## 8. Pay-to-Script Hash

## 9. 区块，Blocks

