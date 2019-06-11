#include <regex.h>
#include <stdio.h>
#include <string.h>

#define BUFSIZE 512

int main( int argv, char* args[] )
{
    int i, j, start_pos, end_pos, final_pos;
    char in[100] = "test:'S2F15' W";

    const char regex[] = "(.+):'S([0-9]+)F([0-9]+)'";
    regex_t regexBuffer;
    regmatch_t patternMatch[4];
    const size_t pat_count = 4;

    FILE* fp;
    char line_buf[BUFSIZE];


    if (regcomp(&regexBuffer, regex, REG_EXTENDED | REG_NEWLINE) != 0) {
        printf("regex compile failed\n");
        return 1;
    }

    if ((fp = fopen("data.txt", "r")) == NULL) {
        printf("file open error\n");
        return 1;
    }

    while (fgets(line_buf, BUFSIZE, fp) != NULL) {
        if (strchr(line_buf, ':') == NULL) continue;

        if (regexec(&regexBuffer, line_buf, pat_count, patternMatch, 0) != 0) {
            printf("No match\n");
            return 1;
        }

        final_pos = 0;
        for (i = 0; i<pat_count; i++) {
            start_pos = patternMatch[i].rm_so;
            end_pos = patternMatch[i].rm_eo;
            if (start_pos == -1 || end_pos == -1) {
                break;
            }
            for (j = start_pos; j < end_pos; j++) {
                printf("%c", line_buf[j]);
            }
            printf("\n");
        }
        
        line_buf[strlen(line_buf)-1] = '\0';
        printf("Remaining[%s]\n", &line_buf[patternMatch[0].rm_eo]);
    }
    fclose(fp);
    
    regfree(&regexBuffer);
    return 0;
}