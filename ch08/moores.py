import matplotlib.pyplot as plt

POS = [year for year in range(1970, 2025)]
MOORES = [1000 * (2 ** (i * 0.5)) for i in range(len(POS))]
plt.plot(POS, MOORES)


DATA = (
    ('Intel 4004', 2_250, 1971),
    ('Motorola 68000', 68_000, 1979),
    ('Intel Pentium', 3_100_000, 1993),
    ('Intel Itanium', 25_000_000, 2001),
    ('Intel Core i7', 730_000_000, 2008),
    ('AMD Zen', 4_800_000_000, 2017),
    ('Apple M1', 16_000_000_000, 2020),
    ('Apple M4', 28_000_000_000, 2024),
)

data_x = [x for label, y, x in DATA]
data_y = [y for label, y, x in DATA]
plt.plot(data_x, data_y, 'v')
for label, y, x in DATA:
    plt.text(x, y, label)


plt.gca().grid()
plt.yscale('log')

plt.show()
