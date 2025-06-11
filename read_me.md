本文是一个简易教程，1.安装labelme标注自制的数据集；2.自制符合coco格式的数据集，方便使用一些框架（detectron）内置的coco相关函数；3.使用detectron框架，mask2former的网络结构，训练一个分割模型

# 一.安装labelme,完成图片数据标注，并转化为json格式标注  
## 1 安装labelme  
推荐在windows下安装，因为labelme在linux下gui容易报错  
### 1.1 下载 anaconda  
从官网或者清华源下载并安装到本地  
### 1.2 安装labelme  
先创造环境,python版本不要太高，容易报错  
conda create --name labelme python=3.6 -y  
激活环境后，安装必要依赖  
conda install pyqt  
conda install pillow  
安装labelme  
pip install labelme  
安装成功后，在终端输入labelme,会启动程序。  
### 1.3 使用labelme 标注数据  
左边栏 open dir打开待标记的图片集。  
使用create polygons标点法框出目标物体的轮廓，轮廓首尾相连后会自动跳出label框，输入label名，如有需要可以输入group id，可从同类物体中区分出个体。  
我们在标注时，一类物体使用同一个label。需要标注的类别（需要预警的18类险情）事先定义好，整个训练流程前后要保持一致。  
完成后crtl s保存到目标文件夹，labelme会自动生成一个与原图文件名一的json文件。  
# 二。将labelme的json文件按coco数据集格式组织  
# 1 安装panopticapi  
## 1.1  
git clone https://github.com/cocodataset/panopticapi.git  
这个文件夹很重要，后面要改变其中一些文件，使用者如果有别的需求，也可以自己改写  
pip install -e panopticapi  
安装panopticapi这个工具  
# 2 转化为instance annotation  
将labelme生成的.json文件放到一个文件夹中,并copy上面git clone 的panopticapi文件夹下的panoptic_coco_categories.json文件。然后运行gather.ipynb文件，记得将文件中的路径改成自己的。此时就会得到符合coco数据集结构的instance annotations.json。如果你要新增一些categories ，记得改写gather.ipynb中的new_categories字典
gather.ipynb会生成categerie.json和instance_train.json两个文件，记得注意修改路径。
随后为了以防万一，记得运行check_duplicate_colors.py，检查color不要重复。
简单说明一下，panopticapi后续会将color与annotation id双射绑定，所以重复会把不同的物体混淆。当然上述只针对thing，对于stuff，在coco数据集中多为背景，大多彼此不可区分，所以，stuff是color与categories_id绑定，当然这也不可以混淆。

# 3 根据categries.json文件生成metadata.json，方便后面注册文件夹。
使用我提供的categories2meta.py文件，记得修改其中的路径。coco默认的有一个stuff类是things,但在categories中没有，所以我手动添加了它。生成的metadata.json文件是为了下面注册数据集时使用，如果你改变了生成的json文件的路径或者名字，你可能需要对应修改下面提供的注册代码。

# 4 将instance.json 转化为 panoptic.json
用我提供的detection2panoptic_coco_format.py  文件 替换 ./panopticapi/converters/detection2panoptic_coco_format.py 注意几个路径，可以在文件中搜索todo。 然后执行。
python ./panopticapi/converters/detection2panoptic_coco_format.py --input_json_file ./custom_coco/annotations/instance_train.json --output_json_file ./custom_coco/annotations/panoptic_train.json --categories_json_file ./custom_coco/categories.json

input、output路径记得改成自己的，categories_json是2中gather.ipynb文件生成的，结合了我们自定义的类和coco本身的数据类。

此时 需要的数据已经备全，但仍需要按照mask2former需要的格式组织一下文件目录。可以参考Mask2Former/datasets/README.md
大致如下：
--custom_coco
----annotations
------instance_train.json
------panoptic_train.json
----panoptic_train        # dir 全景标注的彩色png mask
----train                 # dir 未被标注的原图
----panoptic_semseg_train # dir 用于语义分割，黑白掩码,我上面的代码会生成，但好像有问题，生成的不是黑白，而是灰度图，如果你要训练语义分割，请自行更改./panopticapi/converters/detection2panoptic_coco_format.py

# 5 png -> jpg
coco格式的数据集，图片必须是.jpg，如果你是.png，我提供了一个png2jpg.ipynb文件供你进行格式转化。

# 6 将上面生成的custom_coco 文件夹移动到 Mask2Former/datasets目录下

# 三、注册自定义数据集，训练mask2former
值得一说的是，我构建了两个conda环境，一个labelme py 3.6 一个 mask2former py 3.8，建议你也创建两个，避免冲突
## 先创建conda环境，python=3.8
conda create -n mask2former python=3.8 -y
conda activate mask2former

## 使用系统安装的11.1的cuda，系统默认是12.1，这一步的cuda和下面安装pytorch的cudatoolkit版本要保持一致，否则编译detectron会出错
echo 'export CUDA_HOME=/usr/local/cuda-11.1' >> ~/.bashrc
echo 'export PATH=/usr/local/cuda-11.1/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-11.1/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
## 这一步可以用nvcc --version来检查上面路径设置是否正确，同时如果你使用的不是91服务器，记得nvidia-smi检查你系统驱动的cuda版本向下兼容cuda11.1（高版本兼容低版本）

## 安装pytorch trochvision cudatoolkit(gpu版本)
conda install pytorch==1.10.0 torchvision==0.11.1 cudatoolkit=11.1 -c pytorch -c nvidia
## 终端输入下面指令检查安装是否正确
python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available())"
输出应该如下
1.10.0 11.1 True

## 安装一些依赖库
conda install numpy
pip install -U opencv-python
conda install -c conda-forge libxcrypt

## 更新gcc g++版本到9.5.0
conda install -c conda-forge gcc_linux-64=9 gxx_linux-64=9
安装后，如果which gcc指向系统/usr/bin/gcc而不是conda环境目录下，最好更改一下路径,否则gcc --version可能不会改变
#创建软连接
ln -sf $CONDA_PREFIX/bin/x86_64-conda-linux-gnu-gcc $CONDA_PREFIX/bin/gcc
ln -sf $CONDA_PREFIX/bin/x86_64-conda-linux-gnu-g++ $CONDA_PREFIX/bin/g++
#改变路径
echo 'export PATH=$CONDA_PREFIX/bin:$PATH' >> ~/.bashrc
echo 'export CC=$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-gcc' >> ~/.bashrc
echo 'export CXX=$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-g++' >> ~/.bashrc

source ~/.bashrc
再激活环境，gcc/g++ --version 检查是否为9.5.0

## 安装detectron
下面的指令under your working directory e.g. /data/lmy/
git clone git@github.com:facebookresearch/detectron2.git
cd detectron2
pip install -e .
如果成功安装
python -c "import detectron2; print(detectron2.__version__)"
应该输出0.6
(到这一步，我已经复现过一次，理论上不会有问题，如果有，请详询gpt或者detectron的官网)

## 安装一些处理数据集的工具
pip install git+https://github.com/cocodataset/panopticapi.git
(如果你从头到尾按read_me.md配置环境，那你应该在上面git clone 过并且安装过panopticapi)
pip install git+https://github.com/mcordts/cityscapesScripts.git
## 安装mask2former
下面的指令under your working directory e.g. /data/lmy/
git clone git@github.com:facebookresearch/Mask2Former.git
cd Mask2Former
pip install -r requirements.txt
cd mask2former/modeling/pixel_decoder/ops
sh make.sh
python -c 'import MultiScaleDeformableAttention;print(MultiScaleDeformableAttention.__file__);print("success install MultiScaleDeformableAttention")'

## run
### 注册自定义数据集(训练前和推理前各一次)
代码参见register.py，请把它加到demo.py train_net.py的一开头：

如果你要注册一个支持语义分割训练的数据集，使用下面的函数
detectron2.data.datasets.register_coco_panoptic_separated(name, metadata, image_root, panoptic_root, panoptic_json, sem_seg_root, instances_json)
其中多了一个参数sem_seg_root:directory which contains all the ground truth segmentation annotations.

### 训练
进入Mask2Former/
python /data/lmy/mask2Former/train_net.py --config-file /data/lmy/mask2Former/configs/coco/panoptic-segmentation/swin/my.yaml --num-gpus 1

### 推理
进入Mask2Former/demo/
python demo.py --config-file ../configs/coco/panoptic-segmentation/swin/my.yaml --input 9.png --output output_dir --opts MODEL.WEIGHTS ckpt_path

上面指令中的具体路径 记得改成自己的路径
注意mask2former的很多设置，例如batch_size lr都是基于8 gpu设计的，如果你改变了num-gpus，可能就要自己寻找最合适的超参了
其余具体使用细节可以看Mask2Former/GETTING_STARTED.md
