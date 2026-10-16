/* Local test instrumentation, never linked into a distribution build. */
#include <sandbox.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char **argv) {
    if (argc < 2) return 64;
    char *error = NULL;
    const char *profile = "(version 1)(allow default)"
        "(deny network-outbound (remote ip \"*:*\"))"
        "(allow network-outbound (remote ip \"localhost:*\"))";
    if (sandbox_init(profile, 0, &error) != 0) {
        fprintf(stderr, "sandbox_init: %s\n", error ? error : "unknown error");
        return 78;
    }
    const char *vars[] = {"DYLD_ROOT_PATH", "DYLD_INSERT_LIBRARIES",
        "DYLD_LIBRARY_PATH", "DYLD_FRAMEWORK_PATH", "DYLD_SHARED_CACHE_DIR", "DYLD_SHARED_REGION"};
    for (int i = 0; i < 6; i++) {
        char name[128];
        snprintf(name, sizeof(name), "TAVERNA_SAVED_%s", vars[i]);
        const char *value = getenv(name);
        if (value) setenv(vars[i], value, 1);
        unsetenv(name);
    }
    setenv("TAVERNA_SANDBOX_APPLIED", "1", 1);
    execv(argv[1], argv + 1);
    perror("sandboxed simulator exec");
    return 78;
}
