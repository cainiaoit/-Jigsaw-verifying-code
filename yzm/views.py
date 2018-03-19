# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import random
import cv2,os
from io import StringIO,BytesIO
from django.http import HttpResponse
from matplotlib import pylab
import time
import md5
import uuid
import numpy as np
from json import loads, dumps
#https://www.lfd.uci.edu/~gohlke/pythonlibs/
from matplotlib.pyplot import imsave


def ssid():
    t=time.time()
    s=random.randint(1000,100000)
    m1 = md5.new()   
    m1.update("{0}{1}".format(t,s))
    return m1.hexdigest()

#通过最大宽高获取四条边的边距
def bj(image):
    #四边边距
    z_s="0*0"
    z_x="0*%s"%image[0]
    y_s="%s*0"%image[1]
    y_x="%s*%s"%(image[0],image[1])

#图片转为二进制
def pt_ejz(img):
    #将opencv的三维矩阵通过matplotlib绘图储存到缓存里
    buffer = BytesIO()
    #由于matplotlib绘图是bgr进行rgb转换
    if len(cv2.split(img)) != 4:
        b,g,r = cv2.split(img)
        img_back2 = cv2.merge([r,g,b])
        imsave(buffer,img_back2,"png")
        bjt=buffer.getvalue()
    else:

        b,g,r,a = cv2.split(img)

        img_back2 = cv2.merge([r,g,b,a])
        imsave(buffer,img_back2,"png")
        bjt=buffer.getvalue()
    return bjt
    
tp=dict()

def my_image(request,ssid_num):
    #随机获取背景图
    image_dir="{0}/img".format(os.getcwd())
    
    img_name="{0}/{1}.jpg".format(image_dir,random.randint(1,3))
    print(img_name)
    
    #图像尺寸变换
    fbl=[500,500]
    image=cv2.resize(cv2.imread(img_name),(fbl[0],fbl[1]),interpolation=cv2.INTER_CUBIC)

    #随机出要拼图的位置
    wide_image=random.randint(fbl[0]/2,fbl[0])
    high_image=random.randint(fbl[1]*0.5,fbl[1])
    
    #将拼图生成为区域放入背景图
    
    #提取拼图
    img=cv2.imread("%s/pt/pt3.bmp"%os.getcwd())
    rows,cols,channels = img.shape
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #将图像提取,图像色度小于150的设置为255白色
    blurred = cv2.blur(gray, (9, 9))
    (_, thresh) = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY)
    

    #加载透明图
    img_back_pt=cv2.imread("%s/pt/1.png"%os.getcwd(),cv2.IMREAD_UNCHANGED)
    img_fbl=img_back_pt.shape
    img_back_pt_fbl=[img_fbl[0],img_fbl[1]]
    print img_back_pt_fbl
    
    # draw a bounding box arounded the detected barcode and display the image
    #cv2.imshow('image',thresh)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    


    
    #遍历替换
    
    center=[wide_image,high_image]#在新背景图片中的位置
    html_center=[]
    for i in range(rows):
        for j in range(cols):
            if thresh[i,j]==255:#这里设置成上面替换的颜色
                #拼图
                #添加通道Alpha值为0,代表百分百透明
                s=image[center[0]-i,center[1]-j].tolist()
                s.append(255)
                a=np.array(s)

                img_back_pt[img_back_pt_fbl[0]-i,img_back_pt_fbl[1]-j]=a
                html_center=[center[0]-i,center[1]-j]
                image[center[0]-i,center[1]-j]=img[i,j]#此处替换颜色，为BGR通道
    

    
    #将opencv的三维矩阵通过matplotlib绘图储存到缓存里

    bj=pt_ejz(image)
    pt=pt_ejz(img_back_pt)
#    cv2.imwrite(buffer, img_back)
    

 #   cv2.imshow('image',img_back_pt)
 #   cv2.waitKey(0)
 #   cv2.destroyAllWindows()
    
        
    print html_center
    tp[ssid_num]={'bjt':bj,'pt':pt,'xs':html_center}
    
    return ssid_num
    
def bjt(request):
    if 'yzm_ssid' in request.COOKIES:
        ssid_num=request.COOKIES.get('yzm_ssid', None)
        return HttpResponse(tp[ssid_num]['bjt'],content_type="image/png")
    else:
        ssid_num = ssid()
        response = HttpResponse(tp[ssid_num]['bjt'],content_type="image/png")
        response.set_cookie("yzm_ssid",ssid_num)
        sx(request,ssid_num)
        
        return response

def pt(request):

    if 'yzm_ssid' in request.COOKIES:
        ssid_num=request.COOKIES.get('yzm_ssid', None)
        return HttpResponse(tp[ssid_num]['pt'],content_type="image/png")
    else:
        ssid_num = ssid()
        response = HttpResponse(tp[ssid_num]['pt'],content_type="image/png")
        
        response.set_cookie("yzm_ssid",ssid_num)
        sx(request,ssid_num)
        
        return response
    
    

def sx(request,ssid_num):
    return my_image(request,ssid_num)

@csrf_exempt
def index_post(request):
    end=''
    #判断id和客户端是否有加载拼图验证码
    if 'yzm_ssid' in request.COOKIES :
        ssid_num=request.COOKIES.get('yzm_ssid', None)
        
        if 'xs' in tp[ssid_num] and request.POST.get('html_x',None) != None:
            
            server_xy=tp[ssid_num]['xs']
            html_left=int(request.POST.get('html_x',None).replace('px',''))
            html_top=int(request.POST.get('html_y',None).replace('px',''))
            print html_top, html_left
            x=server_xy[0]-html_top
            y=server_xy[1]-html_left
            
            #边距差距正负18以内
            if 18 > x and 0 < x+18  and 18 > y and 0 < y + 18 :
                end='ok'
            else:
                end ='error'
    else:
        end='error'
    status={'status':end,'txt':""}
    status=dumps(status)
    return HttpResponse(status, content_type='application/json')
    
def index(request):
    
    if 'yzm_ssid' not in request.COOKIES:
        response = render(request, 'html/yzm.html')
        ssid_num = ssid()
        response.set_cookie("yzm_ssid",ssid_num)
    else:
        ssid_num=request.COOKIES.get('yzm_ssid', None)
        response = render(request, 'html/yzm.html')
    #http://blog.csdn.net/baidu_25343343/article/details/53215193
    sx(request,ssid_num)
    
    return response

def demo(request):
    
    return render(request, 'html/demo.html')
