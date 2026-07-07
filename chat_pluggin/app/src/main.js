import { meet } from '@googleworkspace/meet-addons/meet.addons';

export async function initializeSidePanel() {
    const session = await meet.addon.createAddonSession({
        cloudProjectNumber: '969049321776'
    });
    // Signals Meet that loading is complete
    return await session.createSidePanelClient();
}

export async function initializeMainStage() {
    const session = await meet.addon.createAddonSession({
        cloudProjectNumber: '969049321776'
    });
    return await session.createMainStageClient();
}