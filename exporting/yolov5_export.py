import os
import torch
import sys
from torch.onnx import TrainingMode
import yaml
import argparse
import kqat

import torchvision
from torch.utils.tensorboard import SummaryWriter
from torchvision import datasets, transforms
import numpy as np
from PIL import Image
from numpy import asarray

sys.path.insert(0, './detection/yolov5/yolov5')
os.chdir("detection/yolov5/yolov5")

from yolov5.yolov5_runner import Yolov5Runner

# Writer will output to ./runs/ directory by default
# writer = SummaryWriter()

def save_weight(num_classes): 
    current_path=os.getcwd()
    par_path = os.path.dirname(current_path)
    sys.path.append(os.path.join(par_path, 'yolov5'))
    from models.yolo import Model  
    num_classes = num_classes 
    device=torch.device('cpu')
    ckpt = torch.load(path, map_location=device)
    model = Model(yaml_path, nc=num_classes)
    ckpt['model'] = {k: v for k, v in ckpt['model'].float().state_dict().items() if k in model.state_dict() and model.state_dict()[k].shape == v.shape}
    model.load_state_dict(ckpt['model'])
    torch.save(model.state_dict(),pt_path,_use_new_zipfile_serialization=False)

    
def export_onnx(input_h, input_w, num_classes):

    onnx_batch_size, onnx_img_h, onnx_img_w, num_classes = 1, input_h, input_w, num_classes
    yolov5_model = Yolov5Runner(model_path=pt_path, yaml_path=yaml_path, grid20_path=grid20_path, grid40_path=grid40_path, grid80_path=grid80_path, num_classes=num_classes, imgsz_h=onnx_img_h, imgsz_w=onnx_img_w, conf_thres=0.001, iou_thres=0.65, top_k_num=3000, vanish_point=0.0) 
    
    # Input
    img = torch.zeros((onnx_batch_size, 3, onnx_img_h, onnx_img_w))  
    # img = img.type(torch.cuda.FloatTensor)

    # Load PyTorch model
    model = yolov5_model.yolov5_model
    model.eval()
    model.model[-1].export = True  # set Detect() layer export=True
    y = model(img)  # dry run



    # for n_iter in range(100):
    #     writer.add_scalar('Loss/train', np.random.random(), n_iter)
    #     writer.add_scalar('Loss/test', np.random.random(), n_iter)
    #     writer.add_scalar('Accuracy/train', np.random.random(), n_iter)
    #     writer.add_scalar('Accuracy/test', np.random.random(), n_iter)

    # grid = torchvision.utils.make_grid(img)
    # writer.add_image('images', grid, 0)
    # writer.add_graph(model, img)
    # writer.close()    

    # ONNX export
    try:
        import onnx
        print('\nStarting ONNX export with onnx %s...' % onnx.__version__)
        print('****onnx file****',onnx_export_file)
        torch.onnx.export(model, img, onnx_export_file, verbose=False, opset_version=11, keep_initializers_as_inputs=True, input_names=['images'], output_names=['classes', 'boxes'] if y is None else ['output'], training=TrainingMode.PRESERVE)
        # Checks
        onnx_model = onnx.load(onnx_export_file)  # load onnx model
        onnx.checker.check_model(onnx_model)  # check onnx model
        print(onnx.helper.printable_graph(onnx_model.graph))  # print a human readable model
        print('ONNX export success, saved as %s' % onnx_export_file)
    except Exception as e:
        print('ONNX export failure: %s' % e)
    model.name = 'yolov5s'
    dataset = kqat.get_distill_dataset(model, (3, onnx_img_h, onnx_img_w), num_batch=1,
        batch_size=16, num_workers=16, refine_cycle=1000, debug=True)
    dataset.save("./zeroqyolodata")

    # img, labels = next(iter(dataset))
    # grid = torchvision.utils.make_grid(img)
    # writer.add_image('images', grid, 0)
    # writer.close()    



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default='../yolov5/data/pretrained_paths_520.yaml', help='the path to pretrained model paths yaml file')

    args = parser.parse_args()
    
    with open(args.data) as f:
        data_dict = yaml.load(f, Loader=yaml.FullLoader)  # data dict
        
    os.environ["CUDA_VISIBLE_DEVICES"] = '0'
    num_classes = data_dict['nc']
    input_w = data_dict['input_w']
    input_h = data_dict['input_h']
    grid_dir = data_dict['grid_dir']
    grid20_path = data_dict['grid20_path']
    grid40_path = data_dict['grid40_path']
    grid80_path = data_dict['grid80_path']
    path = data_dict['path']
    pt_path=data_dict['pt_path']
    yaml_path=data_dict['yaml_path']
    onnx_export_file = data_dict['onnx_export_file']
    # save_weight(num_classes)

    export_onnx(input_h, input_w, num_classes)






