import kfp
from kfp import dsl
import kfp.components as components
from kfp.components import func_to_container_op


# Define component functions
def download_evaluation_files(output: components.OutputPath(), evaluation_dataset_path: str, model_uid: str,
                              model_access_token: str, host: str, port: str, access_key: str, secret_key: str):
    import os
    from mitlab_aiml_tools.auth.credential import CredentialServer
    from mitlab_aiml_tools.pipeline.file import FileUtility

    credential_server = CredentialServer(
        host=host,
        port=port,
        access_key=access_key,
        secret_key=secret_key
    )
    file_manager = FileUtility(credential_manager=credential_server)

    # download training dataset
    downloaded_dataset = file_manager.download(
        file_type="dataset", file_path=evaluation_dataset_path)

    # download pretrain model
    pretrain_model = file_manager.download(
        file_type="model",
        model_uid=model_uid,
        model_access_token=model_access_token
    )

    # save download training dataset and pretrain model to output path
    download_folder_path = output
    download_dataset_path = f"""{output}/training_dataset.zip"""
    download_model_path = f"""{output}/pretrain_model.zip"""
    os.makedirs(download_folder_path, exist_ok=True)
    with open(download_dataset_path, "wb") as file:
        file.write(downloaded_dataset.content)
    with open(download_model_path, "wb") as file:
        file.write(pretrain_model.content)


def evaluation(input: components.InputPath(), output: components.OutputPath()):
    import os
    import json
    from mitlab_aiml_tools.pipeline.compress import CompressionUtility

    ############################# User import insert here #############################
    {{  user_import | indent(4)  }}
    ####################################### End #######################################

    # decompress training dataset and pretrain model in input path
    training_dataset_input_path = f"""{input}/training_dataset.zip"""
    pretrain_model_input_path = f"""{input}/pretrain_model.zip"""
    training_dataset_folder_path = "./training_dataset/"
    pretrain_model_folder_path = "./pretrain_model/"
    training_dataset_file_path = "./training_dataset/{{ pipeline_settings.basic.input_dataset_filename }}"
    pretrain_model_file_path = "./pretrain_model/{{ pipeline_settings.basic.input_model_filename }}"

    os.makedirs(training_dataset_folder_path, exist_ok=True)
    CompressionUtility.decompress(
        compressed_file_path=training_dataset_input_path, extract_path=training_dataset_folder_path)

    os.makedirs(pretrain_model_folder_path, exist_ok=True)
    CompressionUtility.decompress(
        compressed_file_path=pretrain_model_input_path, extract_path=pretrain_model_folder_path)

    ############################## User code insert here ##############################
    {{  user_code | indent(4)  }}
    ####################################### End #######################################

    filename = f"""{output}/metrics"""
    folder_path = output
    os.makedirs(folder_path, exist_ok=True)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({{ pipeline_settings.basic.output_metrics_variable }}, f, ensure_ascii=False, indent=4)


def upload_metrics(input: components.InputPath(), model_uid: str, host: str, port: str, access_key: str,
                   secret_key: str):
    from mitlab_aiml_tools.auth.credential import CredentialServer
    from mitlab_aiml_tools.pipeline.metrics import MetricUtility
    import json

    # initial credential
    credential_server = CredentialServer(
        host=host,
        port=port,
        access_key=access_key,
        secret_key=secret_key
    )
    print(credential_server)
    metric_manager = MetricUtility(credential_manager=credential_server)

    metrics_file_path = f"""{input}/metrics"""

    with open(metrics_file_path, 'r') as f:
        metrics = json.load(f)

    # upload metrics
    print('Metrics will be uploaded to', model_uid)
    r = metric_manager.upload_accuracy(
        model_uid=model_uid,
        model_accuracy=metrics["{{ pipeline_settings.basic.output_metrics_type }}"]
    )
    print(r)


download_training_dataset_op = func_to_container_op(
    download_evaluation_files, base_image=img_name_map["download_evaluation_files"])
retrain_op = func_to_container_op(
    evaluation, base_image=img_name_map["evaluation"])
upload_model_op = func_to_container_op(
    upload_metrics, base_image=img_name_map["upload_metrics"])


@dsl.pipeline(
    name='pipeline',
    description='pipeline example'
)
def pipeline(evaluation_task_uid: str, evaluation_dataset_path: str, model_uid: str, model_access_token: str, host: str,
             port: str, access_key: str, secret_key: str):
    task1 = download_training_dataset_op(evaluation_dataset_path=evaluation_dataset_path,
                                         model_uid=model_uid,
                                         model_access_token=model_access_token,
                                         host=host,
                                         port=port,
                                         access_key=access_key,
                                         secret_key=secret_key)
    task1.set_cpu_request('{{ pipeline_settings.advanced.download_evaluation_files.set_cpu_request }}')\
        .set_cpu_limit('{{ pipeline_settings.advanced.download_evaluation_files.set_cpu_limit }}')
    task1.set_memory_request('{{ pipeline_settings.advanced.download_evaluation_files.set_memory_request }}') \
        .set_memory_limit('{{ pipeline_settings.advanced.download_evaluation_files.set_memory_limit }}')
    task1.set_ephemeral_storage_request(
        '{{ pipeline_settings.advanced.download_evaluation_files.set_ephemeral_storage_request }}') \
        .set_ephemeral_storage_limit(
        '{{ pipeline_settings.advanced.download_evaluation_files.set_ephemeral_storage_limit }}')
    task1.set_caching_options({{ pipeline_settings.advanced.download_evaluation_files.set_caching_options }})
    task1.set_image_pull_policy('{{ pipeline_settings.advanced.download_evaluation_files.set_image_pull_policy }}')
    task1.add_pod_label(evaluation_task_uid, 'download_evaluation_files')


    task2 = retrain_op(input=task1.output)
    task2.set_cpu_request('{{ pipeline_settings.advanced.evaluation.set_cpu_request }}') \
        .set_cpu_limit('{{ pipeline_settings.advanced.evaluation.set_cpu_limit }}')
    task2.set_memory_request('{{ pipeline_settings.advanced.evaluation.set_memory_request }}') \
        .set_memory_limit('{{ pipeline_settings.advanced.evaluation.set_memory_limit }}')
    task2.set_ephemeral_storage_request(
        '{{ pipeline_settings.advanced.evaluation.set_ephemeral_storage_request }}') \
        .set_ephemeral_storage_limit(
        '{{ pipeline_settings.advanced.evaluation.set_ephemeral_storage_limit }}')
    task2.set_caching_options({{pipeline_settings.advanced.evaluation.set_caching_options}})
    task2.set_image_pull_policy('{{ pipeline_settings.advanced.evaluation.set_image_pull_policy }}')
    task2.add_pod_label(evaluation_task_uid, 'evaluation')


    task3 = upload_model_op(input=task2.output, model_uid=model_uid,
                            host=host, port=port, access_key=access_key, secret_key=secret_key)
    task3.set_cpu_request('{{ pipeline_settings.advanced.upload_metrics.set_cpu_request }}') \
        .set_cpu_limit('{{ pipeline_settings.advanced.upload_metrics.set_cpu_limit }}')
    task3.set_memory_request('{{ pipeline_settings.advanced.upload_metrics.set_memory_request }}') \
        .set_memory_limit('{{ pipeline_settings.advanced.upload_metrics.set_memory_limit }}')
    task3.set_ephemeral_storage_request(
        '{{ pipeline_settings.advanced.upload_metrics.set_ephemeral_storage_request }}') \
        .set_ephemeral_storage_limit(
        '{{ pipeline_settings.advanced.upload_metrics.set_ephemeral_storage_limit }}')
    task3.set_caching_options({{pipeline_settings.advanced.upload_metrics.set_caching_options}})
    task3.set_image_pull_policy('{{ pipeline_settings.advanced.upload_metrics.set_image_pull_policy }}')
    task3.add_pod_label(evaluation_task_uid, 'upload_metrics')


if __name__ == '__main__':
    kfp.compiler.Compiler().compile(pipeline, 'pipeline.yaml')