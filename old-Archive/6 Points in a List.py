# This is a student points registration program in a list:
# First, the user is asked how many entries there are to register, then the program queries each student's information and saves it in a list,
# finally all the lists are collected into a main list:

main_List=[]
individual_List=[]                                      
copy_container=[]
i=1

n=int(input("How many student information will you register? "))
while i<=n:
    name=input("Enter the Student name: ")
    individual_List.append(name)
    point=float(input("Enter the point: "))
    individual_List.append(point)
    copy_container=individual_List.copy()
    print(i,"/",n," is entered.")
    i+=1
    main_List.append(copy_container)
    individual_List.clear()
print("\nThe final list:\n",main_List,"\n")