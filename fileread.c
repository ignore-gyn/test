/*
 * fileread.c
 *
 *  Created on: 2017/09/12
 *      Author: GYN
 */

#include <stdio.h>
#include <stdlib.h>

int main(void) {

	FILE* fp;
	const char fname[] = "data.txt";
	fp = fopen(fname, "r");
	if (fp == NULL) {
		printf("File open error\n");
		return 1;
	}

	printf("%s open\n", fname);

	char line[256][256];
	char tmp[256];
	int i = 0;
	while (fgets(line[i], 256, fp) != NULL) {
		if (sscanf(line[i], "T1 %s\n", tmp) == 1) {
			printf("T1 found\n");
			snprintf(line[i], 256, "T1 %s\n", "T1");

		} else if (sscanf(line[i], "T3 %s", tmp) == 1) {
			printf("T3 found\n");
			printf("%s\n", tmp);
			snprintf(line[i], 256, "T3 %s\n", "T3");

		} else if (sscanf(line[i], "T2 %s", tmp) == 1) {
			printf("T2 found\n");
			snprintf(line[i], 256, "T2 %s\n", "T2");
		}
		printf("%d\n", i);
		i++;
	}

	fclose(fp);

//	fseek(fp, 0, SEEK_SET);

	fp = fopen(fname, "w");
	if (fp == NULL) {
		printf("File open error\n");
		return 1;
	}

	int j = 0;
	while (j < i) {
		fprintf(fp, "%s", line[j]);
		printf("%d: %s\n", j, line[j]);
		j++;
	}

	fclose(fp);
	return 0;
}

