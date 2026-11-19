def find_number(numbers, target):
    for i in range(len(numbers)):
        if numbers[i] == target:
            return i

    return -1


numbers = [10, 25, 30, 45]
target = 30

result = find_number(numbers, target)
print(result)