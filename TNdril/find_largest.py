def find_largest(numbers):
    if numbers == []:
        return None

    largest = numbers[0]

    for number in numbers:
        if number > largest:
            largest = number
        
    return largest
    

numbers = [10, 5, 2, 18]


result = find_largest(numbers)
print(result)