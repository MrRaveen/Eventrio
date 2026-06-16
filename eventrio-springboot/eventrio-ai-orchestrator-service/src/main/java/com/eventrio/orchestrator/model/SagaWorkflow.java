package com.eventrio.orchestrator.model;

import com.eventrio.common.enums.SagaWorkflowStatusEnum;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.Field;

import java.time.Instant;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "saga_workflow")
public class SagaWorkflow {

    @Id
    private String id;

    private String userID;

    private String eventID;

    @Builder.Default
    private SagaWorkflowStatusEnum status = SagaWorkflowStatusEnum.PROCESSING;

    @Field("created_timestamp")
    @Builder.Default
    private Instant createdTimestamp = Instant.now();

    @Field("ending_timestamp")
    private Instant endingTimestamp;
}
