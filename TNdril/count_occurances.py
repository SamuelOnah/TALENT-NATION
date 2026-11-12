def count_occurrences(numbers, target):
    counter = 0
    for number in numbers:
        if number == target:
            counter = counter + 1 
    
    return counter

print(count_occurrences([2, 5, 2, 8, 2], 2))
print(count_occurrences([1, 4, 7], 10))