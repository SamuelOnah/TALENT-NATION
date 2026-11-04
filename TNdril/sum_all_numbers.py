def  list_sum(numbers):
    total = 0
    for number in numbers:
        total = total + number
    return total

numbers = [2, 4, 6, 8]

result = list_sum(numbers)
print(result)