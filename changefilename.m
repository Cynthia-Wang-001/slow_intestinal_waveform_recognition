% % Configuration
% target_dir = 'N:\matlab_for_gi\data_edited';
% suffix = '_0226';
% keywords = {'fast', 'postprandial'};
% 
% % Initialize counters and log
% file_list = dir(target_dir);
% file_list = file_list(~[file_list.isdir]); % Filter out directories
% rename_log = struct('OldName', {}, 'NewName', {});
% 
% % Counters for each keyword
% counters = containers.Map(keywords, [1, 1]);
% 
% fprintf('--- Renaming Process Started ---\n');
% 
% for i = 1:length(file_list)
%     old_full_name = file_list(i).name;
%     [~, ~, ext] = fileparts(old_full_name);
%     lower_name = lower(old_full_name);
% 
%     match_found = false;
%     for k = 1:length(keywords)
%         key = keywords{k};
% 
%         if contains(lower_name, key)
%             % Generate new name with 3-digit padding
%             idx = counters(key);
%             new_base_name = sprintf('%s_%03d%s', key, idx, suffix);
%             new_full_name = [new_base_name, ext];
% 
%             % Execute rename
%             movefile(fullfile(target_dir, old_full_name), ...
%                      fullfile(target_dir, new_full_name));
% 
%             % Update log and counters
%             rename_log(end+1).OldName = old_full_name;
%             rename_log(end).NewName = new_full_name;
%             counters(key) = idx + 1;
% 
%             % Print result
%             fprintf('%s -> %s\n', old_full_name, new_full_name);
%             match_found = true;
%             break; 
%         end
%     end
% 
%     if ~match_found
%         fprintf('Skipped (no keyword): %s\n', old_full_name);
%     end
% end
% 
% fprintf('--- Renaming Process Completed ---\n');


% % Configuration
% target_dir = 'N:\matlab_for_gi\data_edited'; % Update this path if the second folder is different
% suffix = '_0305';
% keywords = {'fast', 'postprandial', 'postpradial'};
% 
% % Initialize counters with specific starting values
% % fast starts at 11, postprandial/postpradial starts at 5
% start_values = [11, 5, 5]; 
% counters = containers.Map(keywords, start_values);
% 
% % Initialize file list and log
% file_list = dir(target_dir);
% file_list = file_list(~[file_list.isdir]); 
% rename_log = struct('OldName', {}, 'NewName', {});
% 
% fprintf('--- Renaming Process Started (Custom Start) ---\n');
% 
% for i = 1:length(file_list)
%     old_full_name = file_list(i).name;
%     [~, ~, ext] = fileparts(old_full_name);
%     lower_name = lower(old_full_name);
% 
%     match_found = false;
%     for k = 1:length(keywords)
%         key = keywords{k};
% 
%         if contains(lower_name, key)
%             idx = counters(key);
% 
%             % Use the standard 'postprandial' label even if 'postpradial' was found
%             label = key;
%             if strcmp(key, 'postpradial')
%                 label = 'postprandial';
%             end
% 
%             new_base_name = sprintf('%s_%03d%s', label, idx, suffix);
%             new_full_name = [new_base_name, ext];
% 
%             % File operation
%             movefile(fullfile(target_dir, old_full_name), ...
%                      fullfile(target_dir, new_full_name));
% 
%             % Logging
%             rename_log(end+1).OldName = old_full_name;
%             rename_log(end).NewName = new_full_name;
% 
%             % Increment specific counter
%             counters(key) = idx + 1;
% 
%             fprintf('%s -> %s\n', old_full_name, new_full_name);
%             match_found = true;
%             break; 
%         end
%     end
% end
% 
% fprintf('--- Renaming Process Completed ---\n');


%% 1. 配置信息
target_dir = 'N:\data_part2\new_2'; % 新数据所在的文件夹
suffix = '_0305';                   % 今天的日期后缀
keywords = {'fast', 'postprandial', 'postpradial'};

% 重点：根据你已有数据量设置起始值
% 已有 20个 fast -> 新的从 21 开始
% 已有 12个 postprandial -> 新的从 13 开始
start_values = [21, 13, 13]; 
counters = containers.Map(keywords, start_values);

%% 2. 初始化
file_list = dir(target_dir);
file_list = file_list(~[file_list.isdir]); % 过滤掉文件夹
rename_log = struct('OldName', {}, 'NewName', {});

fprintf('--- 正在开始重命名过程 (接续上次编号) ---\n');

%% 3. 循环处理
for i = 1:length(file_list)
    old_full_name = file_list(i).name;
    
    % 跳过已经是新格式的文件或日志文件
    if contains(old_full_name, suffix) || contains(old_full_name, 'xlsx')
        continue;
    end
    
    [~, ~, ext] = fileparts(old_full_name);
    lower_name = lower(old_full_name);
    
    match_found = false;
    for k = 1:length(keywords)
        key = keywords{k};
        
        if contains(lower_name, key)
            % 统一标签名（修正拼写错误）
            label = 'postprandial';
            if strcmp(key, 'fast')
                label = 'fast';
            end
            
            % 获取当前编号
            % 注意：为了防止 postpradial 和 postprandial 序号打架，我们手动同步它们
            if strcmp(label, 'postprandial')
                idx = counters('postprandial');
            else
                idx = counters('fast');
            end
            
            % 生成新文件名
            new_base_name = sprintf('%s_%03d%s', label, idx, suffix);
            new_full_name = [new_base_name, ext];
            
            % 执行重命名操作
            try
                movefile(fullfile(target_dir, old_full_name), ...
                         fullfile(target_dir, new_full_name));
                
                % 更新日志
                rename_log(end+1).OldName = old_full_name;
                rename_log(end).NewName = new_full_name;
                
                % 更新计数器 (同步更新 postprandial 和 postpradial)
                if strcmp(label, 'postprandial')
                    counters('postprandial') = idx + 1;
                    counters('postpradial') = idx + 1;
                else
                    counters('fast') = idx + 1;
                end
                
                fprintf('成功: %s -> %s\n', old_full_name, new_full_name);
                match_found = true;
            catch ME
                fprintf('错误: 无法重命名 %s, 原因: %s\n', old_full_name, ME.message);
            end
            break; 
        end
    end
    
    if ~match_found
        fprintf('跳过 (未发现关键词): %s\n', old_full_name);
    end
end

%% 4. 保存记录表
if ~isempty(rename_log)
    log_table = struct2table(rename_log);
    log_name = fullfile(target_dir, ['Rename_Log', suffix, '.xlsx']);
    writetable(log_table, log_name);
    fprintf('--- 任务完成！---\n');
    fprintf('新生成的记录表已保存至: %s\n', log_name);
else
    fprintf('--- 未发现需要重命名的文件 ---\n');
end