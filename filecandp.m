%% 1. 设置路径
sourceDir = 'N:\matlab_for_gi';           % 源文件夹
targetDir = 'N:\matlab_for_gi\data_edited'; % 目标文件夹


%% 2. 获取所有 .mat 文件列表
fileList = dir(fullfile(sourceDir, '*.mat'));
copyCount = 0;

fprintf('开始筛选并复制文件...\n');

%% 3. 循环处理
for i = 1:length(fileList)
    fileName = fileList(i).name;
    
    % 使用正则表达式匹配关键词 (regexpi 是不区分大小写的)
    % 'fasting|postprandial' 表示匹配 fasting 或者 postprandial
    if ~isempty(regexpi(fileName, 'fasting|postprandial'))
        
        sourcePath = fullfile(sourceDir, fileName);
        targetPath = fullfile(targetDir, fileName);
        
        % 执行复制操作
        [status, msg] = copyfile(sourcePath, targetPath);
        
        if status
            fprintf('已成功复制: %s\n', fileName);
            copyCount = copyCount + 1;
        else
            fprintf('复制失败: %s，错误信息: %s\n', fileName, msg);
        end
    end
end

%% 4. 结果反馈
fprintf('\n处理完成！\n');
fprintf('共扫描文件总数: %d\n', length(fileList));
fprintf('共成功复制文件: %d\n', copyCount);