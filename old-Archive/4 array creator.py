from array import *

def readArray(arrayName1,maxMember):
    arrayName=array('i',[])
    for i in range(0,maxMember):
        arrayName.append(int(input("Enter a Number: ")))
    return arrayName

def printArray(arrayName2):
    for i in arrayName2:
        print(i, end=" ")

def changeSort(r,maxMem):
    for i in range(0,maxMem-1):
        for j in range(i+1,maxMem):
            if r[i]>r[j]:
                r[i],r[j]=r[j],r[i]

def MyArray():
    a=array('i',[])
    n=int(input("Enter your desired length for the array: "))
    a=readArray(a,n)
    printArray(a)
    changeSort(a,n)
    print("\nThe sorted version is: ")
    printArray(a)

MyArray()