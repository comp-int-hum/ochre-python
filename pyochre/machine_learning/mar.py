import os.path
import subprocess
import shlex


def create_huggingface_mar(args):
    hf_org, hf_name = args.huggingface_model_name.split("/")
    hf_url = "https://huggingface.co/{}/{}".format(hf_org, hf_name)
    base_path = os.path.join(
        args.ochre_path,
        "temp",
        "huggingface_repos",
        hf_org
    )
    os.makedirs(base_path, exist_ok=True)    
    repo_path = os.path.join(base_path, hf_name)

    if not os.path.exists(repo_path):
        pid = subprocess.Popen(
            shlex.split("git clone {}".format(hf_url)),
            cwd=base_path
        )
        pid.communicate()

    m = AutoModel.from_pretrained(repo_path)
    p = AutoProcessor.from_pretrained(repo_path)
    t = AutoTokenizer.from_pretrained(repo_path)
    c = AutoConfig.from_pretrained(repo_path)
    f = AutoFeatureExtractor.from_pretrained(repo_path)
    i = AutoImageProcessor.from_pretrained(repo_path)
    b = AutoBackbone.from_pretrained(repo_path)
    
    # cmd = [
    #     "torch-model-archiver",
    #     "--model-name", args.model_name,
    #     "--version", args.model_version,
    #     "--serialized-file", "{}/pytorch_model.bin".format(path),
    #     "--handler", args.handler,
    #     "--extra-files", "{0}/config.json,{0}/special_tokens_map.json,{0}/tokenizer_config.json,{0}/tokenizer.json".format(path),
    #     "--export-path", path,
    # ]
    # logging.info("invoking '%s'", shlex.join(cmd))
    # pid = subprocess.Popen(cmd)
    # pid.communicate()
    # shutil.move("{}/{}.mar".format(path, args.model_name), args.output)
    # return args.output


def create_mar(args):
    pass
