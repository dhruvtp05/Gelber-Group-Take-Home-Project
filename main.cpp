#include <iostream>
#include <unordered_map>
#include <vector>
#include <string>
#include <sstream>
#include <limits>

struct Product 
{
    long price;
    std::vector<string> inputs
};

std::unordered_map<std::string, Product> products;
std::unordered_map<std::, long> memo;

// parse a price string into actual cents
long parseCents(const std::string& s)
{
    if (s == "null")
    {
        return -1;
    }

    size_t dot = s.find('.');

    if (dot == std::string::npos)
    {
        return std::stol(s) * 100;
    }

    std::string whole = s.substr(0, dot);
    std::string frac = s.substr(dot + 1);

    if (frac.size() == 1)
    {
        frac += "0";
    }

    return std::stol(whole) * 100 + std::stol(frac);
}

// the recursive algorithm to find the minimum cost
long minCost(const std::string& name)
{
    // check memo
    if (memo.count(name))
    {
        return memo[name];
    }

    Product& p = products[name];

    // no inputs means that raw material that must be purchased
    if (p.inputs.empty())
    {
        return memo[name] = p.purchasePrice;
    }

    // sum the cost of building from the inputs
    long buildCost = 0;
    for (const std::string& input : p.inputs)
    {
        buildCost += minCost(input);
    }

    // if unable to purchase, must build
    if (p.purchasePrice == -1)
    {
        return memo[name] = buildCost;
    }

    // otherwise take the cheaper option
    return memo[name] = std::min(buildCost, p.purchasePrice);
}

int main() 
{
    // 1. Read all of the input into a single string, 
    //    while collapsing it into one line
    std::string entireInput;
    std::string line;

    while (std::getline(std::cin, line))
    {
        if (!entireInput.empty())
        {
            entireInput += " ";
        }
        entireInput += line;
    }

    // 2. Parse the target product
    // The target is everything before the first comma, minus the last
    // space-separated token 

    // The first comma belongs to the first product record, so we find it,
    // then backtrack to the last space to isolate the target name
    size_t firstComma = entireInput.find(',');
    std::string beforeFirstComma = entireInput.substr(0, firstComma);

    size_t lastSpace = beforeFirstComma.rfind(' ');
    std::string target = beforeFirstComma.substr(0, lastSpace);

    // The remaining input starts where the first product name begins
    std::string remaining = entireInput.substr(lastSpace + 1);

    // 3. Parse each product record from the remaining input
    // Each record has 4 fields: name, purchasePrice, inputSize, inputList
    std::istringstream ss(remaining);
    std::string token;

    while (ss >> token) {
        // Accumulate tokens into the product name until we hit a comma
        std::string record = token;
        while (record.find(',') == std::string::npos && ss >> token) 
        {
            record += " " + token;
        }

        // Split it on commas to extract the 4 fields
        std::istringstream rs(record);
        std::string name, priceStr, sizeStr, inputsStr;

        std::getline(rs, name, ',');
        std::getline(rs, priceStr, ',');
        std::getline(rs, sizeStr, ',');
        std::getline(rs, inputsStr);  

        Product p;
        p.purchasePrice = parseCents(priceStr);

        // Parse the semicolon-separated input list
        int inputSize = std::stoi(sizeStr);
        if (inputSize > 0) 
        {
            std::istringstream is(inputsStr);
            std::string inp;
            while (std::getline(is, inp, ';')) 
            {
                p.inputs.push_back(inp);
            }
        }

        products[name] = p;
    }


    long result = minCost(target);
    std::cout << result / 100 << "."
              << std::setw(2) << std::setfill('0') << result % 100
              << std::endl;

    return 0;
}