#include <stdlib.h>
#include <math.h>

void* foo(int argc)
{
	size_t size = (size_t)round((cos((double)argc) + 2.0) * 16U);
	return malloc(size);
}

int main(int argc, char* argv[])
{
	return foo(argc) != NULL;
}
