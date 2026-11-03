def find_largest(numbers):
    if numbers == []:
        return None

    largest = numbers[0]

    for number in numbers:
        if number > largest:
            largest = number

    return largest


numbers = [12, 13, 79, 5]

result = find_largest(numbers)
print(result)