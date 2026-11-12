def count_even(numbers):
    count = 0

    for number in numbers:
        if number % 2 == 0:
            count = count + 1
    return count 

print(count_even([1, 2, 3, 4, 6]))
print(count_even([1, 3, 5, 7]))
print(count_even([]))