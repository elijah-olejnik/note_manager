from datetime import datetime

date_fmts = ("%d-%m-%Y", "%Y-%m-%d")
today = datetime.now()
issue_date = None
prompt = f"Enter the deadline date in 'dd-mm-yyyy' or 'yyyy-mm-dd' format: "

print(f"\nToday is {today.strftime(date_fmts[0])}\n")

while True:
    user_input = input(prompt)
    for fmt in date_fmts:
        try:
            issue_date = datetime.strptime(user_input, fmt)
            if issue_date.date() == today.date():
                print("\nThe deadline is today!")
            else:
                difference = (issue_date - today).days
                print(f"\n{abs(difference)} days " + ("after" if difference < 0 else "before") + " the deadline")
            exit()
        except ValueError as e:
            pass
    print("Wrong date format! Try again")