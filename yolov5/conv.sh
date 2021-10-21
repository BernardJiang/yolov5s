#! /bin/bash
pushd .  >/dev/null 2>&1
python -m onnxsim --skip-fuse-bn ./yolov5s_zeroq_640_v3.onnx ./yolov5s_zeroq_640_v3.simplified.onnx 
python /workspace/libs/ONNX_Convertor/optimizer_scripts/pytorch2onnx.py ./yolov5s_zeroq_640_v3.simplified.onnx ./yolov5s_zeroq_640_v3.s1.onnx --no-bn-fusion
# python /workspace/libs/ONNX_Convertor/optimizer_scripts/pytorch2onnx.py ./yolov5s_zeroq_640_v3.onnx ./yolov5s_zeroq_640_v3.s1.onnx --no-bn-fusion
python /workspace/libs/ONNX_Convertor/optimizer_scripts/onnx2onnx.py ./yolov5s_zeroq_640_v3.s1.onnx -o ./yolov5s_zeroq_640_v3.s2.onnx --no-bn-fusion -t --add-bn
popd >/dev/null 2>&1
