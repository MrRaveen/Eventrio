package com.eventrio.orchestrator.model;

import com.eventrio.common.enums.SagaStepStatusEnum;
import com.eventrio.common.enums.SagaStepTypeEnum;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.Field;

import java.util.HashMap;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "saga_steps")
public class SagaStep {

    @Id
    private String id;

    @Field("workflow_ID")
    private String workflowId;

    @Field("step_type")
    private SagaStepTypeEnum stepType;

    @Field("total_time_ms")
    @Builder.Default
    private int totalTimeMs = 0;

    @Field("response_json")
    @Builder.Default
    private Map<String, Object> responseJson = new HashMap<>();

    @Field("step_status")
    @Builder.Default
    private SagaStepStatusEnum stepStatus = SagaStepStatusEnum.PENDING;
}
