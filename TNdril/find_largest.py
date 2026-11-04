def find_largest(numbers):
    if numbers == []:
        return None

    largest = numbers[0]

    for number in numbers:
        if number > largest:
            largest = number

    return largest


numbers= []

result = find_largest(numbers)
print(result)