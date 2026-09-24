## Search State

- **Seed**: 2
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.2085 | 0.24 | ❌ rejected |
| 0 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.5405 | 0.57 | ✅ accepted |

**Proposal policy**: task_score is 0.24 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: push_to_goal
- Frozen realised-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`
- Frozen object start: [0.47139345610991795, -0.0241810627903052, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.47139345610991795, -0.0241810627903052, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: push_box
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.05, 0.05, 0.05]
    mass_kg: 0.1
  - name: goal_marker
    role: target_marker
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.4714, -0.0242, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.47139345610991795, -0.0241810627903052, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0286, -0.1258, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.47139345610991795, -0.0241810627903052, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, -0.15, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=-0.208) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: align_2
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: pull_1
  type: pull
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: -0.208
- **task_score** (E): 0.243
- **fitness_score**: 0.222  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.1787 |
| descend_to_contact | 1.00 | 1.00 | 0.0953 |
| push_to_goal | 0.00 | 1.00 | 0.0003 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.488, 0.021, 0.133) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_contact | descend | 1.00 / step_budget | (0.488, 0.021, 0.133)→(0.485, 0.019, 0.039) | (0.492, -0.018, 0.025)→(0.492, -0.020, 0.025) | 0.139→0.138 | 1.00 / 3.000 | 0.869 | 121.155 |
| push_to_goal | push | 0.00 / guard_failure | (0.488, -0.013, 0.035)→(0.488, -0.014, 0.035) | (0.492, -0.020, 0.025)→(0.496, -0.049, 0.025) | 0.138→0.107 | 1.00 / 4.333 | 25.308 | 36.254 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.333
- lateral_force_integral: None
- approach_alignment: 0.542
- goal_progress: 0.333
- terminal_score: 0.333
- phase_score: 0.268
- phase_breakdown.reach_pre_push_score: 0.157
- phase_breakdown.push_to_goal_score: 0.316

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.294
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.333
- **Median Q (composite search score)**: -0.194
- **K-run variance**: 0.0044
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.403


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `27920116be2b9a598fe307ae470bb0295293d051bb1ef513a0996a4d851f2459`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1a1e2536715050e6c37d8aed13e4ecd62004f6234f1413b07d7b475a233f55c9`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7375,"average_solve_count":80.0,"average_success_count":80.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_height":0.08847,"approach_behind.behind_distance":0.04029,"descend_to_contact.behind_distance":0.03185,"descend_to_contact.descend_height":0.00464,"descend_to_contact.descend_tolerance":0.01784,"push_to_goal.force_threshold":28.869,"push_to_goal.push_speed":0.06804,"push_to_goal.push_stroke":0.23643},"optimized_scores":{"best_composite_score":-0.1357,"best_fitness_score":0.2943,"best_task_score":0.33305},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":58.0,"contact_point_centroid":[0.47054,0.0007,0.0472],"force_p95":255.74761,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":277.15524,"mean_force":160.13377,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.46358,0.00929,0.04732]},{"body_a":"world","body_b":"push_box","contact_count":1170.0,"contact_point_centroid":[0.47201,-0.02417,-7e-05],"force_p95":68.44096,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":195.91346,"mean_force":8.24124,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.461,0.011,0.07996]},{"body_a":"attachment","body_b":"push_box","contact_count":66.0,"contact_point_centroid":[0.46873,-0.01977,0.04312],"force_p95":16.10387,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.51617,"mean_force":3.36598,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.46699,-0.00798,0.03658]},{"body_a":"world","body_b":"push_box","contact_count":106.0,"contact_point_centroid":[0.47685,-0.06093,-0.00015],"force_p95":8.73372,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.41369,"mean_force":2.63748,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.46725,-0.00954,0.03647]},{"body_a":"world","body_b":"push_box","contact_count":2220.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48066,0.00678,0.21188]}],"total_contact_groups":5},"final_pose_error":0.19676,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48097,-0.06607,0.02483],"final_tcp_position":[0.47099,-0.02969,0.03531],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":277.15524,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":555.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2220.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_push","tcp_end":[0.46219,0.01388,0.12316],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10569,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":308.0,"n_steps_budget":600.0,"object_pos_end":[0.47188,-0.02696,0.02517],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12622,"object_to_goal_dist_start":0.12903,"object_z_max":0.02525,"peak_contact_force":1.49753,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1228.0,"raw_peak_contact_force":277.15524,"subtask_id":"reach_pre_push","tcp_end":[0.46499,0.00969,0.03918],"tcp_start":[0.46219,0.01388,0.12316],"tcp_to_object_dist_end":0.03983,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":110.0,"n_steps_budget":1000.0,"object_pos_end":[0.48093,-0.06582,0.02476],"object_pos_start":[0.47188,-0.02696,0.02517],"object_to_goal_dist_end":0.08632,"object_to_goal_dist_start":0.12622,"object_z_max":0.02622,"peak_contact_force":32.51617,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":172.0,"raw_peak_contact_force":32.51617,"subtask_id":"push_to_goal","tcp_end":[0.47099,-0.02969,0.03531],"tcp_start":[0.47093,-0.02942,0.03532],"tcp_to_object_dist_end":0.03893,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e864853e179d3df1b19d9aaa17e18a5fe8c66fe7533fc0dd3a88a693de7416e7`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73171,"average_solve_count":82.0,"average_success_count":82.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_height":0.10204,"approach_behind.behind_distance":0.03358,"descend_to_contact.behind_distance":0.04923,"descend_to_contact.descend_height":0.00544,"descend_to_contact.descend_tolerance":0.01997,"push_to_goal.force_threshold":29.98545,"push_to_goal.push_speed":0.06877,"push_to_goal.push_stroke":0.204},"optimized_scores":{"best_composite_score":-0.19422,"best_fitness_score":0.23578,"best_task_score":0.25751},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":50.0,"contact_point_centroid":[0.43934,-0.021,0.0481],"force_p95":27.07243,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.01446,"mean_force":5.16919,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.43576,-0.00933,0.03726]},{"body_a":"world","body_b":"push_box","contact_count":191.0,"contact_point_centroid":[0.4556,-0.04563,-3e-05],"force_p95":9.28705,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.52795,"mean_force":1.78905,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.4329,-0.00099,0.03803]},{"body_a":"world","body_b":"push_box","contact_count":2116.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.46953,-0.0003,0.2185]},{"body_a":"world","body_b":"push_box","contact_count":1312.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.43329,0.00547,0.08823]}],"total_contact_groups":4},"final_pose_error":0.16158,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.46041,-0.06325,0.02487],"final_tcp_position":[0.443,-0.02825,0.0365],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":34.01446,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":529.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2116.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_push","tcp_end":[0.43935,-0.0006,0.13658],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11633,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":328.0,"n_steps_budget":690.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1312.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_pre_push","tcp_end":[0.42896,0.01191,0.03995],"tcp_start":[0.43935,-0.0006,0.13658],"tcp_to_object_dist_end":0.0507,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":120.0,"n_steps_budget":1000.0,"object_pos_end":[0.46035,-0.06301,0.02483],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.0956,"object_to_goal_dist_start":0.12843,"object_z_max":0.02618,"peak_contact_force":1.17752,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":241.0,"raw_peak_contact_force":34.01446,"subtask_id":"push_to_goal","tcp_end":[0.443,-0.02825,0.0365],"tcp_start":[0.44302,-0.02803,0.03652],"tcp_to_object_dist_end":0.04056,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c820cf29ab3e34ea9695cb40d5aba5de55f3ad951ee91f0df578ae7146ee7727`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27451,"average_solve_count":102.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_height":0.11093,"approach_behind.behind_distance":0.05457,"descend_to_contact.behind_distance":0.03439,"descend_to_contact.descend_height":0.00385,"descend_to_contact.descend_tolerance":0.01309,"push_to_goal.force_threshold":29.65825,"push_to_goal.push_speed":0.01381,"push_to_goal.push_stroke":0.12946},"optimized_scores":{"best_composite_score":-0.29546,"best_fitness_score":0.13454,"best_task_score":0.13772},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":21.0,"contact_point_centroid":[0.56135,0.02532,0.04584],"force_p95":81.23768,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":86.06554,"mean_force":36.3904,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.5606,0.03702,0.04592]},{"body_a":"world","body_b":"push_box","contact_count":1202.0,"contact_point_centroid":[0.55319,0.00092,-1e-05],"force_p95":0.64259,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.81644,"mean_force":0.8844,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.56079,0.04273,0.0903]},{"body_a":"attachment","body_b":"push_box","contact_count":35.0,"contact_point_centroid":[0.55706,0.01674,0.04078],"force_p95":30.12613,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.23146,"mean_force":7.38493,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5556,0.02862,0.03467]},{"body_a":"world","body_b":"push_box","contact_count":108.0,"contact_point_centroid":[0.5503,-0.01097,-7e-05],"force_p95":12.81464,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.04378,"mean_force":2.75145,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.55693,0.03065,0.03539]},{"body_a":"world","body_b":"push_box","contact_count":2540.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.53062,0.02435,0.21931]}],"total_contact_groups":5},"final_pose_error":0.10828,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54691,-0.01986,0.02483],"final_tcp_position":[0.55079,0.01722,0.03336],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":86.06554,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":635.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2540.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_push","tcp_end":[0.56335,0.04911,0.14055],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12545,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":312.0,"n_steps_budget":720.0,"object_pos_end":[0.55296,-0.00082,0.0249],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.1583,"object_to_goal_dist_start":0.16043,"object_z_max":0.02504,"peak_contact_force":0.86562,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1223.0,"raw_peak_contact_force":86.06554,"subtask_id":"reach_pre_push","tcp_end":[0.56072,0.03631,0.03772],"tcp_start":[0.56335,0.04911,0.14055],"tcp_to_object_dist_end":0.04004,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":65.0,"n_steps_budget":1000.0,"object_pos_end":[0.54694,-0.01955,0.02475],"object_pos_start":[0.55296,-0.00082,0.0249],"object_to_goal_dist_end":0.13864,"object_to_goal_dist_start":0.1583,"object_z_max":0.02545,"peak_contact_force":42.23146,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":143.0,"raw_peak_contact_force":42.23146,"subtask_id":"push_to_goal","tcp_end":[0.55079,0.01722,0.03336],"tcp_start":[0.55078,0.01747,0.03336],"tcp_to_object_dist_end":0.03796,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```