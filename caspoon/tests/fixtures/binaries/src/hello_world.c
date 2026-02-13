#include <stdio.h>
#include <stdlib.h>

int helper_function(int a, int b) {
    return a + b;
}

int main(int argc, char *argv[]) {
    printf("Hello, World!\n");
    printf("This is a test binary for caspoon\n");
    
    int result = helper_function(5, 3);
    printf("5 + 3 = %d\n", result);
    
    return 0;
}
