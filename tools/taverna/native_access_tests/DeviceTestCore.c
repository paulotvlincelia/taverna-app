/* Test-only wire driver for the iOS Simulator core. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef void *Controller;
extern void haskell_init(void);
extern char *chat_migrate_init_key(char *, char *, int, char *, int, Controller *);
extern char *chat_migrate_init_device_test(char *, char *, int, char *, int, Controller *);
extern char *chat_send_cmd(Controller, char *);
extern char *chat_close_store(Controller);

static int reply(FILE *output, char *value) {
    if (!value) return 0;
    fprintf(output, "%s\n", value);
    fflush(output);
    free(value);
    return 1;
}

int main(int argc, char **argv) {
    if (argc != 5) return 64;
    FILE *input = fopen(argv[3], "r"), *output = fopen(argv[4], "w");
    if (!input || !output) return 64;
    haskell_init();
    Controller controller = NULL;
    char *key = "fixture-simulator-only-key";
    char *result = strcmp(argv[2], "technical") == 0
        ? chat_migrate_init_device_test(argv[1], key, 1, "yesUp", 0, &controller)
        : chat_migrate_init_key(argv[1], key, 1, "yesUp", 0, &controller);
    if (!reply(output, result) || !controller) return 65;
    char *command = NULL;
    size_t size = 0;
    int ok = 1;
    while (getline(&command, &size, input) != -1) {
        command[strcspn(command, "\r\n")] = '\0';
        if (!*command) break;
        if (!reply(output, chat_send_cmd(controller, command))) {
            ok = 0;
            break;
        }
    }
    free(command);
    free(chat_send_cmd(controller, "/_stop"));
    char *close_error = chat_close_store(controller);
    int closed = close_error && *close_error == '\0';
    free(close_error);
    fclose(input);
    fclose(output);
    return ok && closed ? 0 : 66;
}
