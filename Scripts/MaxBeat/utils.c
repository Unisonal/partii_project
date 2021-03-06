#include "utils.h"
#include <stdlib.h>
#include <string.h>
#include <math.h>

// The factorial function, containing pre-computed values for acceration.
int fact(int n){
    switch (n){
        case 0:
            return 1;
            break;
        case 1:
            return 1;
            break;
        case 2:
            return 2;
            break;
        case 3:
            return 6;
            break;
        case 4:
            return 24;
            break;
        case 5:
            return 120;
            break;
        default:
            return n * fact(n-1);
    }
}

// Calculates the probability of getting a given roll
double prRoll(int* arr){
    //Initialize count
    int count[6];
    for (int i=0; i<6; i++){
        count[i] = 0;
    }

    //ASSERT: arr would have size 5, and values from {1,2,3,4,5,6}.
    for (int i=0; i<5; i++){
        count[arr[i]-1] = count[arr[i]-1] + 1;
    }

    // 5/324 = (5!)/(6^5), for simplicity
    double result = 5.0 / 324;

    for (int i=0; i<6; i++){
        result = result / fact(count[i]);
    }

    return result;
}

// Generates all the possible dice-roll patterns for n dice with d faces (default 6)
// Returning a list of lists
int** dicePatterns(int n){
    //ASSERT: n is in [0,5], temp stores the number of items we need to generate.
    int d = 6, p = 0, buffer[n], terminate[n], rp = 0, temp[] = {1,6,21,56,126,252};
    int** result = calloc(temp[n],sizeof(int*));
    if(n == 0){
        result[0] = calloc(1,sizeof(int));
        return result;
    }

    for (int i=0; i<n; i++){
        buffer[i] = 1;
        terminate[i] = d;
    }

    while (memcmp(buffer, terminate, n*sizeof(int)) != 0){
        result[rp] = malloc(n*sizeof(int));
        for (int j=0; j<n; j++){
            result[rp][j] = buffer[j];
        }
        rp++;

        if (buffer[p] == d){
            while (buffer[p] == d){
                p++;
            }
            buffer[p] = buffer[p] + 1;
            while (p != 0){
                p--;
                buffer[p] = buffer[p + 1];
            }
        }else{
            buffer[p]++;
        }
    }

    result[rp] = malloc(n*sizeof(int));
    for (int j=0; j<n; j++){
        result[rp][j] = terminate[j];
    }

    return result;
}

// This is OBVIOUS
int contains(int* arr, int e, int size){
    for (int i=0; i<size; i++){
        if (arr[i] == e){
            return i;
        }
    }
    return -1;
}

// Generates all possible outcomes of choosing r numbers from [0,1,2...13]
// Order doesn't matter
int** choosePatterns(int r){
    //ASSERT: r is in range [1,12].
    int p = 0, n = 13, buffer[r], terminate[r], rp=0, temp[] = {1,14,90,352,935,1782,2508,2640,2079,1210,506,144,25};
    int** result = calloc(temp[r],sizeof(int*));

    for (int i=0; i<r; i++){
        buffer[i] = r - i - 1;
        terminate[i] = 13 - i - 1;
    }

    while(memcmp(buffer, terminate, r*sizeof(int)) != 0){
        int pos = contains(buffer,0,r);
        if (pos >= 0){
            result[rp] = malloc(r*sizeof(int));
            for (int j=0; j<r; j++){
                if (j == pos){
                    result[rp][j] = -1;
                }else{
                    result[rp][j] = buffer[j];
                }
            }
            rp++;
        }

        result[rp] = malloc(r*sizeof(int));
        for (int j=0; j<r; j++){
            result[rp][j] = buffer[j];
        }
        rp++;

        if (buffer[p] == 12){
            while (buffer[p] + p == 12){
                p++;
            }
            buffer[p] = buffer[p] + 1;
            while (p != 0){
                p = p - 1;
                buffer[p] = buffer[p + 1] + 1;
            }
        }else{
            buffer[p] = buffer[p] + 1;
        }

    }

    result[rp] = malloc(r*sizeof(int));
    for (int j=0; j<r; j++){
        result[rp][j] = terminate[j];
    }

    return result;
}

// A bunch of yahtzee category functions.
// ASSERT: dice is an array of size 5, up is in range [0,63].
int yahtzee(int* dice, int up){
    if ((dice[0] == dice[1]) && (dice[0] == dice[2]) && (dice[0] == dice[3]) && (dice[0] == dice[4])){
        return 50;
    }
    else{
        return 0;
    }
}

int ones(int* dice, int up){
    int count = 0;
    for(int i=0; i<5; i++){
        if (dice[i] == 1){
            count++;
        }
    }

    if ((up != 63) && (count + up >= 63)){
        return count + 35;
    }
    else{
        return count;
    }
}

int twos(int* dice, int up){
    int count = 0;
    for(int i=0; i<5; i++){
        if (dice[i] == 2){
            count += 2;
        }
    }

    if ((up != 63) && (count + up >= 63)){
        return count + 35;
    }
    else{
        return count;
    }
}

int threes(int* dice, int up){
    int count = 0;
    for(int i=0; i<5; i++){
        if (dice[i] == 3){
            count += 3;
        }
    }

    if ((up != 63) && (count + up >= 63)){
        return count + 35;
    }
    else{
        return count;
    }
}

int fours(int* dice, int up){
    int count = 0;
    for(int i=0; i<5; i++){
        if (dice[i] == 4){
            count += 4;
        }
    }

    if ((up != 63) && (count + up >= 63)){
        return count + 35;
    }
    else{
        return count;
    }
}

int fives(int* dice, int up){
    int count = 0;
    for(int i=0; i<5; i++){
        if (dice[i] == 5){
            count += 5;
        }
    }

    if ((up != 63) && (count + up >= 63)){
        return count + 35;
    }
    else{
        return count;
    }
}

int sixes(int* dice, int up){
    int count = 0;
    for(int i=0; i<5; i++){
        if (dice[i] == 6){
            count += 6;
        }
    }

    if ((up != 63) && (count + up >= 63)){
        return count + 35;
    }
    else{
        return count;
    }
}

int sum(int* dice){
    int result = 0;
    for(int i=0; i<5; i++){
        result += dice[i];
    }
    return result;
}

int three_of_a_kind(int* dice, int up){
    int count[] = {0, 0, 0, 0, 0, 0};
    for(int i=0; i<5; i++){
        count[dice[i] - 1]++;
    }
    for(int i=0; i<6; i++){
        if (count[i] >= 3){
            return sum(dice);
        }
    }
    return 0;
}

int four_of_a_kind(int* dice, int up){
    int count[] = {0, 0, 0, 0, 0, 0};
    for(int i=0; i<5; i++){
        count[dice[i] - 1]++;
    }
    for(int i=0; i<6; i++){
        if (count[i] >= 4){
            return sum(dice);
        }
    }
    return 0;
}

int fullhouse(int* dice, int up){
    int count[] = {0, 0, 0, 0, 0, 0};
    for(int i=0; i<5; i++){
        count[dice[i] - 1]++;
    }
    if ((contains(count,2,6) >= 0) && (contains(count,3,6) >= 0)){
        return 25;
    }
    else{
        return 0;
    }
}

int small_straight(int* dice, int up){
    if ((contains(dice,1,5) >= 0) && (contains(dice,2,5) >= 0) && (contains(dice,3,5) >= 0) && (contains(dice,4,5) >= 0)){
        return 30;
    }
    else if ((contains(dice,2,5) >= 0) && (contains(dice,3,5) >= 0) && (contains(dice,4,5) >= 0) && (contains(dice,5,5) >= 0)){
        return 30;
    }
    else if ((contains(dice,3,5) >= 0) && (contains(dice,4,5) >= 0) && (contains(dice,5,5) >= 0) && (contains(dice,6,5) >= 0)){
        return 30;
    }
    else{
        return 0;
    }
}

int large_straight(int* dice, int up){
    if ((contains(dice,1,5) >= 0) && (contains(dice,2,5) >= 0) && (contains(dice,3,5) >= 0) && (contains(dice,4,5) >= 0) && (contains(dice,5,5) >= 0)){
        return 40;
    }
    else if ((contains(dice,2,5) >= 0) && (contains(dice,3,5) >= 0) && (contains(dice,4,5) >= 0) && (contains(dice,5,5) >= 0) && (contains(dice,6,5) >= 0)){
        return 40;
    }else{
        return 0;
    }
}

int chance(int* dice, int up){
    return sum(dice);
}

// Code a score state uniquely.
// -1 represents the state with all categories filled.
int code(int* cats, int up, int size){
    // ASSERT: size is the size of array that cats points to.
    if (size == 13){
        return -1;
    }
    
    int result = 0;
    for(int i=0; i<size; i++){
        result += pow(2, cats[i]+1);
    }
    result = result * 64 + up;
    return result;
}

int* append(int* cats, int c, int size){
    int* result = malloc(sizeof(int)*(size+1));
    for (int i=0; i<size; i++){
        result[i] = cats[i];
    }
    result[size] = c;
    return result;
}


// Adds d in array dice, preserving the order.
int* extendDice(int* dice, int d, int size){
    // ASSERT: size is the size of array that dice points to.
    int* result = malloc(sizeof(int)*(size+1));
    int pos = -1, i = 0;
    while (pos < 0){
        if (i == 0){
            if (d >= dice[0]){
                pos = 0;
            }
        }else if(i == size){
            pos = size;
        }else{
            if( (dice[i-1] >= d) && (dice[i] <= d)){
                pos = i;
            }
        }
        i++;
    }

    for(int j=0; j<=size; j++){
        if(j < pos){
            result[j] = dice[j];
        }else if(j == pos){
            result[j] = d; 
        }else{
            result[j] = dice[j-1];
        }
    }

    return result;
}

// Removes d in array dice, preserving the order.
int* removeDice(int* dice, int d, int size){
    // ASSERT: size is the size of array that dice points to.
    int temp = contains(dice, d, size);
    if(temp >= 0){
        int* result = malloc(sizeof(int)*(size - 1));
        for(int i=0; i<size; i++){
            if(i < temp){
                result[i] = dice[i];
            }else if(i > temp){
                result[i-1] = dice[i];
            }
        }
        return result;
    }
    return NULL;
}

int find(int** lib, int* row, int row_size, int entries){
    for (int i=0; i<entries; i++){
        int found = 0;
        for(int j=0; j<row_size; j++){
            if (row[j] == lib[i][j]){
                found++;
            }
        }

        if (found == row_size){
            return i;
        }
    }
    return -1;
}
