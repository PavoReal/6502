import os
import logging
import platform
import subprocess
import re
import concurrent.futures
from math import floor
import enum
import sys

class BuildType(enum.Enum):
    DEBUG   = 0
    RELEASE = 1

compiler = "clang++";

build_type      = BuildType.DEBUG;
logging_level   = logging.INFO;
src_dir         = [r"./sw/src/"];
build_dir       = r"./sw/build/";
clean_build_dir = True;
exe_name        = "6502";

clang_flags       = ["-march=native", "-std=c++20", "-Wall", "-Wextra", "-Werror"];
clang_flags_debug = ["-g", "-O0", "-DDEBUG"];
clang_flags_rel   = ["-flto", "-O3", "-DNDEBUG"];

clang_ld_flags       = [];
clang_ld_flags_debug = ["-g"];
clang_ld_flags_rel   = ["-flto", "-O3"];

src_extentions = [".cpp"];

logging.basicConfig(level=logging_level, format='%(asctime)s - %(levelname)s - %(message)s', );

def is_directory_empty(directory_path):
    return len(os.listdir(directory_path)) == 0;

def get_cpp_compiler_path():
    compiler_path = None;

    if platform.system() == "Windows":
        logging.fatal("Find cpp compiler in windows is not implemented yet.");
        return compiler_path;

    # Find clang in the users path
    try:
        compiler_path = subprocess.check_output(["which", compiler]).decode("utf-8");
        compiler_path = compiler_path.strip();
    except:
        logging.error("Could not find clang in path.");
    
    return compiler_path;
 
def get_cpp_compiler_version(compiler_path):
    compiler_version = None;

    if platform.system() == "Windows":
        logging.fatal("Find cpp compiler version in windows is not implemented yet.");
        return compiler_version;

    # Get compiler version from --version
    try:
        compiler_version = subprocess.check_output([compiler_path, "--version"]).decode("utf-8");
        compiler_version = re.search(r"version\s([0-9]+\.[0-9]+\.[0-9]+)", compiler_version).group(1);
    except:
        logging.error("Could not determine compiler version.");

    return compiler_version;

def get_cpp_compiler_flags_from_config(config):
    if config is None:
        logging.warn("No compile config specified. Couldn't create compiler flags.");
        return [];
    
    compiler_flags_result = [];

    compiler_flags       = config["compiler_flags"];
    compiler_flags_debug = config["compiler_flags_debug"];
    compiler_flags_rel   = config["compiler_flags_rel"];

    if compiler_flags is None:
        logging.warning("No compiler flags specified.");
        compiler_flags = [];
    
    if compiler_flags_debug is None:
        logging.debug("No compiler debug flags specified.");
        compiler_flags_debug = [];
    
    if compiler_flags_rel is None:
        logging.debug("No compiler release flags specified.");
        compiler_flags_rel = [];
    
    compiler_flags_result = compiler_flags;

    if build_type == BuildType.DEBUG:
        compiler_flags_result += compiler_flags_debug;
    elif build_type == BuildType.RELEASE:
        compiler_flags_result += compiler_flags_rel;

    return compiler_flags_result;

def get_ld_flags_from_config(config):
    if config is None:
        logging.warn("No compile config specified. Couldn't create linker flags.");
        return [];

    ld_flags_result = [];

    ld_flags       = config["ld_flags"];
    ld_flags_debug = config["ld_flags_debug"];
    ld_flags_rel   = config["ld_flags_rel"];

    if ld_flags is None:
        logging.warning("No linker flags specified.");
        ld_flags = [];
    
    if ld_flags_debug is None:
        logging.debug("No linker debug flags specified.");
        ld_flags_debug = [];
    
    if ld_flags_rel is None:
        logging.debug("No linker release flags specified.");
        ld_flags_rel = [];
    
    ld_flags_result = ld_flags;

    if build_type == BuildType.DEBUG:
        ld_flags_result += ld_flags_debug;
    elif build_type == BuildType.RELEASE:
        ld_flags_result += ld_flags_rel;

    return ld_flags_result;

def get_src_files_list(src_dir: list):
    file_list = [];

    for dir in src_dir:
        logging.info("Searching for source files in " + dir);

        if not os.path.isdir(dir):
            logging.error("Could not find source directory " + dir);
            continue;
    
        for root, dirs, files in os.walk(dir):
            for file in files:
                for ext in src_extentions:
                    if file.endswith(ext):
                        full_path = os.path.join(root, file);
                        file_list.append(full_path);
                        logging.info("Found " + full_path);

    return file_list;

def compile_src_file(compile_config: dict, flags: list, file: str):
    compiler_path = compile_config["compiler_path"];
    
    file_name = os.path.basename(file);
    output_path = compile_config["build_dir"] + file_name + ".o";
    output_command = ["-c", "-o", output_path];
    
    if (compile_config["obj_file_list"] is not None):
        compile_config["obj_file_list"].append(output_path);

    command = [compiler_path] + output_command + flags + [file];

    if logging_level == logging.DEBUG:
       logging.debug("Compiling " + file + " with command " + str(command));
    else:
        logging.info("Compiling " + file);

    try:
        subprocess.run(command, check=True, capture_output=True);

    except subprocess.CalledProcessError as ex:
        logging.error("Could not compile " + file);
        
        print(ex.stderr.decode("utf-8"), file=sys.stderr);
        

def compile_src_files(compile_config):
    compiler_path = compile_config["compiler_path"];

    if compiler_path is None:
        logging.fatal("No compiler path specified.");
        return;

    flags = get_cpp_compiler_flags_from_config(compile_config);
    logging.info("Using compiler flags " + str(flags));

    src_file_list = compile_config["src_files_list"];

    if  src_file_list is None or len(src_file_list) == 0:
        logging.fatal("No source files specified.");
        return;

    logging.debug("Using " + str(compile_config["thread_count"]) + " threads to compile.");

    futures = [];

    with concurrent.futures.ThreadPoolExecutor(max_workers=compile_config["thread_count"], thread_name_prefix="6502_sw_compile") as executor:
        for file in src_file_list:
            futures.append(executor.submit(compile_src_file, compile_config, flags, file));

    return;

def link_object_files(compile_config):
    ld_path = compile_config["ld_path"];

    if ld_path is None:
        logging.fatal("No linker path specified.");
        return;

    ld_flags = get_ld_flags_from_config(compile_config);
    logging.info("Using linker flags " + str(ld_flags));

    obj_file_list = compile_config["obj_file_list"];

    if obj_file_list is None or len(obj_file_list) == 0:
        logging.fatal("No object files specified. TODO Create list if not specified.");
        return;

    output_path = compile_config["build_dir"] + compile_config["executable_name"];
    output_command = ["-o", output_path];

    command = [ld_path] + output_command + ld_flags + obj_file_list;
    logging.debug("Linking object files with command " + str(command));

    try:
        logging.info("Linking " + output_path);
        subprocess.run(command, check=True, capture_output=True);
    except subprocess.CalledProcessError as ex:
        logging.error("Could not link object files.");
        logging.error("Linker output: " + str(ex.stdout));

    return;

if __name__ == "__main__":
    # 1. Find c++ compiler
    compiler_path = get_cpp_compiler_path();

    if compiler_path is None:
        raise Exception("Could not find c++ compiler.");
    else:
        logging.info("Found c++ compiler at " + compiler_path);

    # 2. Print compiler info
    compiler_version = get_cpp_compiler_version(compiler_path);

    if compiler_version is None:
        logging.error("Could not determine c++ compiler version.");
    else:
        logging.debug("c++ compiler version is " + compiler_version);

    # 3. Find source files
    src_files_list = get_src_files_list(src_dir);


    if len(src_files_list) == 0:
        logging.info("No source files found. Exiting.");
        exit(0);

    logging.debug("Found " + str(len(src_files_list)) + " total source files.");

    compile_config = {};
    compile_config["compiler_path"]        = compiler_path;
    compile_config["compiler_flags"]       = clang_flags;
    compile_config["compiler_flags_debug"] = clang_flags_debug;
    compile_config["compiler_flags_rel"]   = clang_flags_rel;
    compile_config["ld_path"]              = compiler_path;
    compile_config["ld_flags"]             = clang_ld_flags;
    compile_config["ld_flags_debug"]       = clang_ld_flags_debug;
    compile_config["ld_flags_rel"]         = clang_ld_flags_rel;
    compile_config["build_dir"]            = build_dir;
    compile_config["clean_build_dir"]      = clean_build_dir;
    compile_config["src_files_list"]       = src_files_list;
    compile_config["thread_count"]         = os.cpu_count();
    compile_config["executable_name"]      = exe_name;
    compile_config["obj_file_list"]        = []; # Will be filled in by compile_src_file

    # Create build dir
    if not os.path.isdir(build_dir):
        os.mkdir(build_dir);

    # 4. Compile source files
    compile_src_files(compile_config);

    # 5. Link object files
    link_object_files(compile_config);

    # if cl_path is None:
    #     raise Exception("Could not find cl.exe");

    # cl_version = get_cl_version(cl_path);

    # if cl_version is None:
    #     logging.warning("Could not determine cl.exe version.");
    # else:
    #     logging.info("Found cl.exe version " + cl_version + " at " + cl_path);
    
    # src_files_base_path = "./sw/src";
    # src_files_list = [];

    # if os.path.isdir(src_files_base_path):
    #     for root, dirs, files in os.walk(src_files_base_path):
    #         for file in files:
    #             if file.endswith(".c"):
    #                 full_path = os.path.join(root, file);
    #                 src_files_list.append(full_path);
    #                 logging.debug("Found " + full_path);
                    
    # logging.info("Found " + str(len(src_files_list)) + " source files.");

    # if len(src_files_list) == 0:
    #     logging.info("No source files found. Exiting.");
    #     exit(0);

    # thread_count = os.cpu_count();

    # if thread_count is None:
    #     thread_count = 1;
    
    # thread_count = max(1, floor(thread_count / 2));

    # logging.info("Using " + str(thread_count) + " worker threads.");
    # logging.info("Using " + str(c_flags) + " as compiler flags.");

    # if not os.path.isdir(build_dir):
    #     os.mkdir(build_dir);
    #     logging.info("Created build directory at " + build_dir);
    # else:
    #     logging.debug("Build directory already exists at " + build_dir);

    #     if clean_build_dir and not is_directory_empty(build_dir):
    #         logging.info("Build directory is not empty. Cleaning.");
    
    #         for root, dirs, files in os.walk(build_dir):
    #             for file in files:
    #                 path = os.path.join(root, file);
    #                 logging.debug("Removing " + path);
    #                 os.remove(path);
                
    #             for dir in dirs:
    #                 path = os.path.join(root, dir);
    #                 logging.debug("Removing " + path);
    #                 os.rmdir(path);

    # with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
    #     for src_file in src_files_list:
    #         logging.info("Building " + src_file);

    #         cmd_to_run = [cl_path] + c_flags + [r'/Fo:' + build_dir] + [src_file];

    #         executor.submit(subprocess.run, cmd_to_run, text=True);

    # cmd_to_run = [cl_path]  + [build_dir + "/*.obj"] + ld_flags + [r'/Fe:./sw/main.exe'];
    # logging.info("Linking " + str(cmd_to_run));
    # subprocess.run(cmd_to_run, text=True);