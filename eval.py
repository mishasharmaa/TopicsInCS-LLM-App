import json
import subprocess

def run_test(bullets):
    p = subprocess.Popen(
        ["python3", "app.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    output = p.communicate(input=bullets)[0]
    return output

if __name__ == "__main__":
    with open("tests.json") as f:
        tests = json.load(f)

    passed = 0
    for t in tests:
        result = run_test(t["input"])
        if t["expect"].lower() in result.lower():
            passed += 1

    print(f"Pass rate: {passed}/{len(tests)}")
