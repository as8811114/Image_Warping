# -*- coding: utf-8 -*-
"""
Created on Fri May  7 16:40:02 2021

@author: as881
"""


import numpy as np
import cv2 as cv
import random as rd
import math


def is_in_poly(p, poly):
    px, py = p
    is_in = False
    for i, corner in enumerate(poly):
        next_i = i + 1 if i + 1 < len(poly) else 0
        x1, y1 = corner
        x2, y2 = poly[next_i]
        if (x1 == px and y1 == py) or (x2 == px and y2 == py): 
            is_in = True
            break
        if min(y1, y2) < py <= max(y1, y2): 
            x = x1 + (py - y1) * (x2 - x1) / (y2 - y1)
            if x == px:  
                is_in = True
                break
            elif x > px: 
                is_in = not is_in
    return is_in


def GetMatrixA(src,dst):
    k = 0 
    mA = np.empty((8,9))
    for i in range(0,8,2):
        tempA = []
        tempB = []
        l = 0
        for j in range(6):
            if j < 2:
                tempA.append(src[k][l])
                l = l + 1
            elif j == 2:
                tempA.append(1)
            else:
                tempA.append(0)
        
        tempA.append(-1 * dst[k][0] * src[k][0])                                            # -xiXi
        tempA.append(-1 * dst[k][0] * src[k][1])                                            # -xiYi
        tempA.append(-1 * dst[k][0])                                                        # -xi
        mA[i] = tempA
        tempB[0:3] = tempA[3:6]
        tempB[3:6] = tempA[0:3]
        tempB.append(-1 * dst[k][1] * src[k][0])                                            # -yiXi
        tempB.append(-1 * dst[k][1] * src[k][1])                                            # -yiYi
        tempB.append(-1 * dst[k][1])                                                        # -yi
        mA[i + 1] = tempB
        k = k + 1
    return mA
#獲得轉換矩陣
def GetTransformMatrix(mA): 
    bT = []                                                                                 #matrix b for Ax = b
    mTrans = np.empty((3,3))                                                                #Transform Matrix
    tA = np.transpose(mA)
    aTA = tA.dot(mA)
    u,sigma,v=np.linalg.svd(aTA)
    k = 0
    for x in u:
        bT.append(x[8])
        k += 1
    coff = 1.0 / bT[8] 
    #Put elements to Transform Matrix
    mTrans[0] = bT[0:3] 
    mTrans[1] = bT[3:6] 
    mTrans[2][0:2] = bT[6:8] 
    mTrans = mTrans.dot(coff)
    mTrans[2][2] = 1.0
    return mTrans
def Warp(w,h,mT,img,imgOrigin):
    



    flag = np.zeros((h,w)) 
    image = np.zeros((h,w,3), np.uint8)

            
    for i in range (imgOrigin.shape[1]):
        for j in range(imgOrigin.shape[0]):
            image[j][i] = imgOrigin[j][i]
    
    
    
    print("Transmapping")
    for i in range (img.shape[1]):
        for j in range(img.shape[0]):
            OP = mT.dot([[i],[j],[1]])
            u, v, w = OP
            indexu = int(u[0] / w[0]) 
            indexv = int(v[0] / w[0])
            
            if(indexu >= image.shape[1]):
                indexu = image.shape[1] - 1
            if(indexv >= image.shape[0]):
                indexv = image.shape[0] - 1          
            if(indexv < 0):
                indexv = 0
            if(indexu < 0):
                indexu = 0
            else:
                flag[indexv][indexu] = 1
                image[indexv][indexu] = img[j][i]
    t = []      
    a = []
    t.append(mT.dot([[0],[0],[1]]))
    t.append(mT.dot([[0],[img.shape[0]],[1]]))
    t.append(mT.dot([[img.shape[1]],[img.shape[0]],[1]]))
    t.append(mT.dot([[img.shape[1]],[0],[1]]))

    for i in range(4):
        ut, vt, wt = t[i]
   
        indexut = int(ut[0] / wt[0]) 
        indexvt = int(vt[0] / wt[0])
        a.append([indexut,indexvt])
    
    poly = a
    print("Filling blank pixel")
    for i in range (image.shape[1]):
        for j in range(image.shape[0]):
            if(not is_in_poly([i,j],poly)):
                continue
   
            else:
                if(flag[j][i] == 1):
                    continue
                if(i - 1 >= 0 and is_in_poly([i - 1,j],poly)):
                    image[j][i] = image[j][i - 1]

                elif(i + 1 < image.shape[1] and is_in_poly([i + 1,j],poly)):             
                    image[j][i] = image[j][i + 1]

                elif(j - 1 >= 0 and is_in_poly([i,j - 1],poly)):             
                    image[j][i] = image[j - 1][i]

                elif(j + 1 <= image.shape[0] and is_in_poly([i ,j + 1],poly)):             
                    image[j][i] =image[j + 1][i]

                    
                elif(i - 1 >= 0 and j + 1 <= image.shape[0] and is_in_poly([i - 1,j + 1],poly)):             
                    image[j][i] = image[j + 1][i - 1]
                 
                elif(i + 1 < image.shape[1] and j - 1 >= 0 and is_in_poly([i + 1,j - 1],poly)):             
                    image[j][i] = image[j - 1][i + 1]
                  
                elif(i + 1 < image.shape[1] and j + 1 <= image.shape[0] and is_in_poly([i + 1,j + 1],poly)):             
                    image[j][i] = image[j + 1][i + 1]
                   
                elif(i - 1 >= 0 and j - 1 >= 0 and is_in_poly([i - 1,j - 1],poly)):             
                    image[j][i] = image[j - 1][i - 1]
        
    
    
    return image


#Main()
def Stitch(photo1,photo2):
    src = []
    dst = []
    
    siftDetector = cv.xfeatures2d.SIFT_create() 
    kp1,res1 = siftDetector.detectAndCompute(photo1,None)
    
    siftDetector = cv.xfeatures2d.SIFT_create() 
    kp2,res2 = siftDetector.detectAndCompute(photo2,None)
    
    matches = cv.BFMatcher().knnMatch(res1,res2, k = 3)
    
    good = []
    maxium = 0
    for m,n,k in matches:
        if m.distance < 0.5 * n.distance and m.distance < 0.5 * k.distance:
            if(m.distance > maxium):
                maxium = m.distance
            good.append([m])
    good.sort(key=lambda x: x[0].distance, reverse=False)
    mindis = good[0][0].distance
    sizeOfCandi = len(good)

    #RANSAC
    aaa = []
    bbb = []
    while(True):
        
        inliers = 0
        outliers = 0

        aaa = []
        bbb = []
        src = []
        dst = []
        print("checking...")
        for i in range(0,4):
            index = rd.randint(0, sizeOfCandi - 1)
            
            x1 = kp1[good[index][0].queryIdx].pt[0]
            y1 = kp1[good[index][0].queryIdx].pt[1]
            aaa.append(kp1[good[index][0].queryIdx])
            dst.append([x1,y1])
            
            x2 = kp2[good[index][0].trainIdx].pt[0]
            y2 = kp2[good[index][0].trainIdx].pt[1]
            bbb.append(kp2[good[index][0].trainIdx])
            src.append([x2,y2])
        qq = np.float32(src)
        bb = np.float32(dst)
        a = cv.getPerspectiveTransform(qq, bb)
        mA = GetMatrixA(src,dst)
        mTrans = GetTransformMatrix(mA)
    
        for x in good:
            x1 = kp2[x[0].trainIdx].pt[0]
            y1 = kp2[x[0].trainIdx].pt[1]
            corPoint = mTrans.dot([[x1],[y1],[1]])
            x2 = kp1[x[0].queryIdx].pt[0]
            y2 = kp1[x[0].queryIdx].pt[1]
            dis = math.sqrt((corPoint[0] - x2) ** 2 + (corPoint[1] - y2) ** 2)
            if(dis <= mindis*0.25):
                inliers += 1
            else:
                outliers += 1
        if(outliers <= 1):
            outliers = 1
        if(inliers /  outliers > 0.98):
            print("Find!")
            break
        
    
    np.set_printoptions(suppress=True)
    img1 = cv.drawKeypoints(photo1,outImage=photo1,keypoints=aaa,color = [237,28,36], flags=cv.DRAW_MATCHES_FLAGS_DEFAULT)
    img2 = cv.drawKeypoints(photo2,outImage=photo2,keypoints=bbb,color = [237,28,36] ,flags=cv.DRAW_MATCHES_FLAGS_DEFAULT)
    
    result = Warp(img1.shape[0] + img2.shape[0],img1.shape[1],mTrans,img2,img1)
    return result

photo1 = cv.imread("./1.bmp",0)
photo2 = cv.imread("./2.bmp",0)
photo3 = cv.imread("./3.bmp",0)
photo4 = cv.imread("./4.bmp",0)
photo5 = cv.imread("./5.bmp",0)


result1 = Stitch(photo1, photo2)

cv.imshow('Stitch2',result1)
result2 = Stitch(result1, photo3)
cv.imshow('Stitch3',result2)
result3 = Stitch(result2, photo4)
cv.imshow('Stitch4',result3)
finalResult = Stitch(result3, photo5)
cv.imshow('result',finalResult)
cv.imwrite('result.bmp',finalResult)
cv.waitKey()

