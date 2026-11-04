def find_smallest(numbers):
    if numbers == []:
        return None

    smallest = numbers[0]

    for number in numbers:
        if number < smallest:
            smallest = number

    return smallest

numbers = [8, 3, 12, 1, 7]

result = find_smallest(numbers)
print(result)