import random
import copy
import time

def bubbleSort(arr):
	n = len(arr)

	for i in range(n):
		for j in range(n-i-1):
			if arr[j] > arr[j+1]:
				arr[j], arr[j+1] = arr[j+1], arr[j]
def selectiontSort(arr):
	n = len(arr)

	for i in range(n):
		minima = i
		for j in range(i, n):
			if arr[j] < arr[minima]:
				minima = j

		arr[i], arr[minima] = arr[minima], arr[i]
def insertionSort(arr):
	n = len(arr)

	for i in range(1, n):
		
		elem = arr[i]
		j = i

		while j >= 0 and elem <= arr[j]:
			arr[j] = arr[j-1]
			j -= 1

		arr[j+1] = elem
def quickSort(arr):
	if len(arr) <= 1:
		return
	qSort(arr, 0, len(arr)-1)
def qSort(arr, start, stop):

	m = arr[(stop + start) //2]
	l, r = start, stop
	
	while l < r :
		while arr[l] < m:
			l+=1
		while arr[r] > m:
			r-=1

		if l <= r:
			arr[l], arr[r] = arr[r], arr[l]
			l+=1
			r-=1
	
	if start < r:
		qSort(arr, start, r)
	if l < stop:
		qSort(arr, l, stop)

def test(f, name):
	print("testing ", name)
	
	test = [1 for i in range(10000)] 
	start = time.time()
	f(test)
	stop = time.time()
	print("[", isSorted(test), "]", name, " - all same ", stop - start)

	test = [i%7 for i in range(10000)] 
	start = time.time()
	f(test)
	stop = time.time()
	print("[", isSorted(test), "]", name, " - similar ", stop - start)

	test = [i for i in range(10000)]
	start = time.time()
	f(test)
	stop = time.time()
	print("[", isSorted(test), "]", name, " - sorted ", stop - start)

	test = makeArray(0)
	start = time.time()
	f(test)
	stop = time.time()
	print("[", isSorted(test), "]", name, " - empty ", stop - start)

	test = makeArray(1)
	start = time.time()
	f(test)
	stop = time.time()
	print("[", isSorted(test), "]", name, " - 1 elem ", stop - start)

	test = makeArray(10000)
	start = time.time()
	f(test)
	stop = time.time()
	print("[", isSorted(test), "]", name, " - 10 000 elem", stop - start)
	print()
def makeArray(n):
	random.seed(17)

	arr = [i for i in range(n)]
	random.shuffle(arr)

	return arr
def isSorted(arr):

	for i in range( len(arr)-1 ):
		if arr[i] > arr[i+1]:
			return False 

	return True

if __name__ == "__main__":

	test(quickSort, "quicksort")
	test(insertionSort, "insertionSort")
	test(selectiontSort, "selectionsort")
	test(bubbleSort, "bubbleSort")

