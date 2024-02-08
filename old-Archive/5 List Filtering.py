# This program holds the first item of any member in the list, and removes all duplicated/repeated members.
# n is a sample list.

n=['This', 'is', 'a', 'is', 'Test', 'This', 'Test', 'is']

Length_List=len(n)-1

for k in range(0,Length_List):
    if k<=Length_List:
        member=n[k]
        j=n.count(member)
        for i in range(Length_List,0,-1):
            if n[i] == member and j > 1:
                n.pop(i)
                j=j-1
                Length_List-=1
print(n)