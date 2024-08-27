data = []

data.append({
    'name':'Thomas',
    'age':9,
})

data.append({
    'name':'Thomas',
    'age':19,
})

data.append({
    'name':'Thomas',
    'age':90,
})

data.append({
    'name':'Thomas',
    'age':5,
})

data = sorted(data, key=lambda x: x.get('age'), reverse=True)

print(data)