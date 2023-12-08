batch_dir=../data/mygpt3/
# Incorrect API key provided: sk-y4HtX***************************************rOLv
OPENAI_API_KEY=sk-y4HtX3nsqpdQtUfZ5g06U9Kz0I8mcVJTwkWpdO566E0VrOLv

# maxinkai api key
# close by remote
# OPENAI_API_KEY=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

# 关闭代理后，提示个人openai api没有配额


python ../self_instruct/bootstrap_instructions.py \
    --batch_dir ${batch_dir} \
    --num_instructions_to_generate 10 \
    --seed_tasks_path ../data/my_seed_tasks.jsonl \
    --engine "davinci" \
    --api_key ${OPENAI_API_KEY} \
