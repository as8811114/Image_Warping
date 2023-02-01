# Image_Wrapping
輸入5張要拼接的圖片1.bmp~5.bmp到同路徑底下
程式會輸出拼接完成的圖片result.bmp

# 實作細節
**實作:**

`	`**步驟1:**

首先我先透過SIFT演算法找出兩張待轉換的圖片的所有特徵點，

![image](https://user-images.githubusercontent.com/43846907/216083862-c9503704-b1ad-48b7-9aca-503604bb014d.png)

`    `**SIFT(尺度不變特徵轉換)演算法:**

SIFT演算法是一只用來偵測圖片特徵點的演算法，SIFT演算法當中具有尺度不變性，旋轉圖片、改變影像亮度、拍攝視角等皆不會影響特徵點的找尋，因為一個點是否為特徵點會因為周圍的光暗程度以及圖片大小程度有所關係，例如有個點可能在整體來看為特徵點，但是若將該點放大到很多倍之後可能會變為一條線視為非特徵點。

**尺度不變性:**

SIFT為了達到尺度不變性最一開始建立尺度空間，將不同尺度下的關鍵點提取出來，而SIFT在定義圖像本身和尺度空間的關係式為![image](https://user-images.githubusercontent.com/43846907/216083906-c1725630-5648-4a9e-b34d-28b955a3f62a.png)

其中*L(x,y,σ)*為尺度空間函數而I(x,y)為圖形的點*G(x,y,σ)*為高斯模糊，透過改變其中*σ*的值來建立出不同模糊程度的圖片，而其中因為L(x,y*σ*)計算過於複雜且DoG結果近似於LoG，因此SIFT演算法當中改用DoG來代替LoG。

其中DOG公式為![image](https://user-images.githubusercontent.com/43846907/216084090-b616011b-26d4-4b37-9392-800a7e210890.png)


DOG透過將兩個相鄰的高斯尺度影像相減來獲得，獲得了DOG之後每一個點都和本層及相鄰兩層的3\*3領域26個點比較，是極值則被選中為潛在的特徵點。

![image](https://user-images.githubusercontent.com/43846907/216084126-47f75d50-9230-470a-b9be-f721920b3208.png)

而因為需要找到所有特徵點中的極值我們必須要有連續的尺度空間，但因為連續的尺度空間是拿不到的，因此SIFT的做法是透過減少取樣來實現 (圖4)，經過實驗表示DOG金字塔當中每一組需要S+2層影像而又因為DOG金字塔是由高斯金字塔而來，因此每組高斯金字塔需要S+3層影像，同一組則代表相同尺寸，而Scale代表不同高斯模糊的影像，而將這些離散的資料透過曲線擬合再插值找出精確的極值點位址(圖5)，如此一來就能夠達到尺度不變性。

![image](https://user-images.githubusercontent.com/43846907/216084171-449d2aa4-e4de-4a1b-927f-f77ebb148e29.png)(圖4)

![image](https://user-images.githubusercontent.com/43846907/216084202-dffc8954-ae9c-4c4c-a93b-84dd597e72c0.png)

**旋轉不變性:**

SIFT達到旋轉不變性的方法就是先將圖片旋轉到主方向，而這個方向是透過圖片的梯度所得到，這樣就能保證座標軸與影像的相對位址保持一致而達到旋轉不變性。

`	`**步驟2:**

`		`做完了SIFT找到特徵點後我就有了第一張圖的特徵點描述子res1 和 第二張圖的特徵點描述子res2，我將他們使用KNN找出兩組特徵點間，最相似的三個特徵點來將他們加入到候選的對齊點當中，透過比對m n k 三點的距離來找出一個距離最短的點數當作候選點放入good陣列裡面。

`	`![image](https://user-images.githubusercontent.com/43846907/216084237-b50a0cca-5fd7-490b-b410-233bc4352442.png)

`	`接下來需要找到一個合適的Projection Matrix來將圖片二的點扭曲對應到圖片一當中，這個Projection Matrix最好能夠挑的夠精準這樣才能夠讓誤差最小，因此這邊需要使用RANSAC演算法來挑出合適的Matrix點。

`	`![image](https://user-images.githubusercontent.com/43846907/216084281-7e1cd968-a4cc-4fa9-90e6-46a1bafda69b.png)

`	`在做RANSAC之前需要先有Projective Mapping Matrix 因此我先計算出所需要的矩陣。

`	`![image](https://user-images.githubusercontent.com/43846907/216084312-6eff643c-2796-4f27-8585-9db15f59ea67.png)

`	`將4組候選點整理成Ax=0的形式，A為上圖的左邊大矩陣而x為右邊A11~A33矩陣，因此我先將左邊矩陣給建立好如下圖。

`	`![image](https://user-images.githubusercontent.com/43846907/216084338-f1c14c30-a369-4291-b8f1-7b46d4ee65c2.png)

`	`建立好矩陣後欲求E=|Ax-y|^2的最小值，|Ax-y|^2 = (Ax-y)^T ( Ax – y )

`	`假設 y = 0 則 E=|Ax|^2 = x^T A^T Ax ，因A^TA 是 symmetric positive semidefine 所以 A^TA 的特徵值都大於0且λ1 <= λ2 <=…. Λq，所以E(x) E(e1) = x^TA^TAx – e1^T A^TA e1  

`			`= λ1u1^2 + … + λquq^2 - λ1

`			`>=λ1(u1^2+ … + uq^2 - 1) = 0

`	`因此使Ex有最小值的eigenvector 就是對應最小的eigenvalue=>e1

`	`因此我用SVD分解得到eigenvalue 再將最小的eigenvector得出

`	`得到矩陣mTrans作為我的Projective Mapping Matrix

`	`![image](https://user-images.githubusercontent.com/43846907/216084371-65a7f4ef-8e30-43f9-a1eb-cc5eb23a1ac4.png)

`	`**步驟三:**

`		`得到矩陣mTrans之後就需要透過RANSAC來驗證我剛剛所帶入的四組		點是否能夠讓大部分的特徵點都能夠對應到初始圖的特徵點。

`		`**RANSAC:**

![image](https://user-images.githubusercontent.com/43846907/216084396-e35bfa8f-d984-4a69-b2cd-09b3f23eaa6b.png)

先隨機從前面所候補的特徵點當中抽取4組點來當作轉換矩陣的等式		來找到我需要的mTrans矩陣，找到mTrans矩陣之後我將第二張圖的

特徵點dot我所算出的mTrans矩陣並且存在corPoint當中，並且透過

平方開根號的方式來計算兩組點的距離dis，若dis小於等於最一開始

所候選1/4特徵點距離，則加入inliers其餘則為outliers，若最後

Inliers比outliers大於98%則判定這次的mTrans矩陣為好的矩陣，若

低於則重複尋找。

![image](https://user-images.githubusercontent.com/43846907/216084456-5ed39736-7172-4695-b152-dd02aaf3eecb.png)

![image](https://user-images.githubusercontent.com/43846907/216084472-a05ad69f-9862-4f03-a337-6f939c829918.png)


**步驟四:**

找到了所需要的矩陣之後我就將兩張圖片透過Warp函式開始將第二

張圖的像素轉移到第一張圖上。

![image](https://user-images.githubusercontent.com/43846907/216084508-fefa6b0f-d2a8-428e-acd4-6b0d5118cf33.png)

![image](https://user-images.githubusercontent.com/43846907/216084520-99a240bd-6925-4c58-b55e-919acdf28608.png)

在Warp函式當中我先將所有的點轉移到第一張圖當中並且將轉移

過去超出範圍的值用邊界值來補，並且在有值的地方將flag設定為1

在後面補缺值的時候可以忽略不做，在補值之前我先將第二張圖的四

個邊界點算出轉移後的四個頂點，這四個頂點用於後面確認是否為在

正確圖片範圍內的四點。

![image](https://user-images.githubusercontent.com/43846907/216084772-f60f3911-2027-4d4a-8c67-5b7aab133472.png)

判斷是否在圖片範圍內的函式如下圖

![image](https://user-images.githubusercontent.com/43846907/216084787-f769afd2-5fb3-4fbd-a22f-d6ab4e5f018e.png)

做完之後我再重新掃描一次圖片，將那些flag為的那些點掃描出來，

並且再去看這個缺值的地方是否是在圖片的範圍裏面，若有的話再去

檢測看看八鄰點是否是可以拿來補值得像素點，若不是則繼續往後找

若有值直接將空缺的pixel中填入鄰邊向素將空缺的點補完後，回傳轉

移過後的image完成影像拼接。

![image](https://user-images.githubusercontent.com/43846907/216084813-97a2a760-c2dc-4eb5-8899-96029ef14953.png)
## 效果圖
![image](https://user-images.githubusercontent.com/43846907/216084871-65ca38a1-b015-4931-b4ba-27160715dda3.png)


