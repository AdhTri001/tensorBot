from time import sleep
from pytz import country_names as cn_pytz
from sqlite3 import connect

country_names = list(cn_pytz.values())
i = 1
line = ""
conn = connect("./data/SideData.sqlite3")

for name in country_names:
    if len(line.rstrip()) > 100:
        print(line.rstrip())
        line = ""
    line += "\033[96m{:>3}.\033[0m {:<34} ".format(i, name.capitalize())
    i += 1

print("Press ctrl+c or cmd+c to exit.")

n = 0
try:
    while True:
        try:
            i = int(input("Enter the number before the country of the city : "))
            if i < 0:
                raise IndexError
            count_name = country_names[i - 1]
        except ValueError:
            print("The city number should be int.", i, "is not an integer.")
            sleep(3)
            continue
        except IndexError:
            print("The number", i, "is not a valid number.")
            sleep(3)
            continue
        city_name = input("Enter the name of city".ljust(48) + ": ").lower()
        conf = input(
            " ".join(
                (
                    "City of name",
                    "'",
                    city_name.capitalize(),
                    "'",
                    "will be registered for country",
                    count_name.capitalize(),
                    "[Y/n]? ",
                )
            )
        )
        if conf.lower() == "y":
            curs = conn.cursor()
            curs.execute(
                "UPDATE country_city SET country_city = ? WHERE country_name = ?",
                (city_name + ",", count_name),
            )
            n += 1
        else:
            print("Its not a yes.")
            sleep(1)
            continue
except KeyboardInterrupt:
    print(f"Okay added {n}", "cities." if n != 1 else "city.")
