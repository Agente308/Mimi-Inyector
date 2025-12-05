#define UNICODE
#include <windows.h>
#include <tlhelp32.h>

#pragma comment(lib, "comdlg32.lib")
#pragma comment(lib, "shell32.lib")

DWORD FindProcessId(const wchar_t* processName) {
    DWORD pid = 0;
    HANDLE hSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hSnap == INVALID_HANDLE_VALUE) return 0;

    PROCESSENTRY32 pe;
    pe.dwSize = sizeof(PROCESSENTRY32);
    if (Process32First(hSnap, &pe)) {
        do {
            if (_wcsicmp(pe.szExeFile, processName) == 0) {
                pid = pe.th32ProcessID;
                break;
            }
        } while (Process32Next(hSnap, &pe));
    }
    CloseHandle(hSnap);
    return pid;
}

bool InjectDLL(DWORD pid, const wchar_t* dllPath) {
    bool result = false;

    HANDLE hProcess = OpenProcess(PROCESS_CREATE_THREAD | PROCESS_QUERY_INFORMATION |
        PROCESS_VM_OPERATION | PROCESS_VM_WRITE | PROCESS_VM_READ, FALSE, pid);

    if (!hProcess) return false;

    size_t dllPathSize = (wcslen(dllPath) + 1) * sizeof(wchar_t);
    LPVOID remoteMem = VirtualAllocEx(hProcess, nullptr, dllPathSize, MEM_COMMIT, PAGE_READWRITE);

    if (!remoteMem) {
        CloseHandle(hProcess);
        return false;
    }

    if (!WriteProcessMemory(hProcess, remoteMem, dllPath, dllPathSize, nullptr)) {
        VirtualFreeEx(hProcess, remoteMem, 0, MEM_RELEASE);
        CloseHandle(hProcess);
        return false;
    }

    LPVOID loadLibAddr = (LPVOID)GetProcAddress(GetModuleHandle(L"kernel32.dll"), "LoadLibraryW");
    if (!loadLibAddr) {
        VirtualFreeEx(hProcess, remoteMem, 0, MEM_RELEASE);
        CloseHandle(hProcess);
        return false;
    }

    HANDLE hThread = CreateRemoteThread(hProcess, nullptr, 0,
        (LPTHREAD_START_ROUTINE)loadLibAddr, remoteMem, 0, nullptr);

    if (hThread) {
        WaitForSingleObject(hThread, INFINITE);
        CloseHandle(hThread);
        result = true;
    }

    VirtualFreeEx(hProcess, remoteMem, 0, MEM_RELEASE);
    CloseHandle(hProcess);
    return result;
}

extern "C" __declspec(dllexport) bool Inject(const wchar_t* dllPath, const wchar_t* processName) {
    DWORD pid = FindProcessId(processName);
    if (pid == 0) return false;
    return InjectDLL(pid, dllPath);
}
