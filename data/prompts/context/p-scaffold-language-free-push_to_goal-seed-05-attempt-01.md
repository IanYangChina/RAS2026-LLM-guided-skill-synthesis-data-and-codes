## Search State

- **Seed**: 5
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4714 | 0.76 | ✅ accepted |
| 0 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4708 | 0.75 | ✅ accepted |

**Proposal policy**: task_score is 0.76 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`
- Frozen object start: [0.5366003508494456, 0.03695289476837925, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5366003508494456, 0.03695289476837925, 0.025)
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
  frozen_object_start: [0.5366, 0.037, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5366003508494456, 0.03695289476837925, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0366, -0.187, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.755, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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
| `object` | offset from object initial position (0.5366003508494456, 0.03695289476837925, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.471) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: contact_detected
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2

```

## Design Metrics

- **Composite score**: 0.471
- **task_score** (E): 0.755
- **fitness_score**: 0.681  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2855 |
| contact_1 | 1.00 | 1.00 | 0.0533 |
| push_1 | 1.00 | 1.00 | 0.1255 |
| retract_1 | 0.00 | 1.00 | 0.1654 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, 0.101, 0.036) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.514, 0.101, 0.036)→(0.514, 0.050, 0.021) | (0.519, 0.022, 0.025)→(0.521, 0.013, 0.025) | 0.173→0.165 | 1.00 / 2.667 | 3.162 | 10.868 |
| push_1 | push | 1.00 / step_budget | (0.514, 0.050, 0.021)→(0.501, -0.074, 0.024) | (0.521, 0.013, 0.025)→(0.512, -0.109, 0.028) | 0.165→0.046 | 1.00 / 4.000 | 54.268 | 93.044 |
| retract_1 | retract | 0.00 / step_budget | (0.501, -0.074, 0.024)→(0.496, 0.071, 0.102) | (0.512, -0.109, 0.028)→(0.508, -0.107, 0.025) | 0.046→0.047 | 1.00 / 4.000 | 0.245 | 43.231 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.423
- goal_progress: 0.967
- terminal_score: 0.967
- phase_score: 0.833
- phase_breakdown.push_score: 0.818
- phase_breakdown.contact_score: 0.867
- phase_breakdown.approach_score: 0.820

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.887
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.967
- **Median Q (composite search score)**: 0.377
- **K-run variance**: 0.0211
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.709


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `7ff7a4e3a1b03e3d7ba3d0b298d1ee8847b5344eb55f2aa0aaf582e7a98ab8ac`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `028a6956ebe09ab7c7952341570355f52da12e46fb22d3462091c70c024324ff`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76623,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.04643,"push_1.push_depth":0.09989,"retract_1.retract_height":0.18038},"optimized_scores":{"best_composite_score":0.36034,"best_fitness_score":0.57034,"best_task_score":0.62418},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":792.0,"contact_point_centroid":[0.54865,-0.01132,0.05485],"force_p95":112.94759,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":126.29475,"mean_force":72.9192,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51771,0.0043,0.02348]},{"body_a":"attachment","body_b":"push_box","contact_count":801.0,"contact_point_centroid":[0.53629,-0.00393,0.05188],"force_p95":100.14086,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":106.44227,"mean_force":54.15748,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51787,0.005,0.02344]},{"body_a":"world","body_b":"push_box","contact_count":1507.0,"contact_point_centroid":[0.54323,-0.04738,-0.0003],"force_p95":75.90937,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":92.23408,"mean_force":49.80805,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51739,0.00231,0.02372]},{"body_a":"push_box","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.54838,-0.06236,0.05581],"force_p95":80.2734,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":89.42649,"mean_force":39.62268,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50651,-0.05159,0.03001]},{"body_a":"world","body_b":"push_box","contact_count":3697.0,"contact_point_centroid":[0.52446,-0.08253,-3e-05],"force_p95":0.24655,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":89.14312,"mean_force":0.48597,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5008,0.0241,0.07079]},{"body_a":"attachment","body_b":"push_box","contact_count":62.0,"contact_point_centroid":[0.52834,-0.05481,0.05977],"force_p95":62.76024,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.9032,"mean_force":22.92087,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50578,-0.04855,0.03098]},{"body_a":"attachment","body_b":"push_box","contact_count":120.0,"contact_point_centroid":[0.53837,0.05775,0.03942],"force_p95":9.89501,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.34177,"mean_force":4.0991,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53126,0.06967,0.02125]},{"body_a":"world","body_b":"push_box","contact_count":2393.0,"contact_point_centroid":[0.53666,0.0353,-1e-05],"force_p95":2.17298,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.67628,"mean_force":0.45667,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52895,0.09145,0.02622]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51292,0.07216,0.17685]}],"total_contact_groups":9},"final_pose_error":0.07244,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52391,-0.08251,0.02499],"final_tcp_position":[0.49864,0.0898,0.10973],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":126.29475,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53035,0.11538,0.03637],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.53851,0.02854,0.02505],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18265,"object_to_goal_dist_start":0.1905,"object_z_max":0.02516,"peak_contact_force":1.70506,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2513.0,"raw_peak_contact_force":11.34177,"tcp_end":[0.53189,0.06526,0.02038],"tcp_start":[0.53035,0.11538,0.03637],"tcp_to_object_dist_end":0.0376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":804.0,"n_steps_budget":900.0,"object_pos_end":[0.5323,-0.08451,0.03122],"object_pos_start":[0.53851,0.02854,0.02505],"object_to_goal_dist_end":0.07328,"object_to_goal_dist_start":0.18265,"object_z_max":0.0313,"peak_contact_force":126.10781,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3100.0,"raw_peak_contact_force":126.29475,"tcp_end":[0.50742,-0.05482,0.0288],"tcp_start":[0.53189,0.06526,0.02038],"tcp_to_object_dist_end":0.03881,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52391,-0.08251,0.02499],"object_pos_start":[0.5323,-0.08451,0.03122],"object_to_goal_dist_end":0.0716,"object_to_goal_dist_start":0.07328,"object_z_max":0.03453,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3803.0,"raw_peak_contact_force":89.42649,"tcp_end":[0.49864,0.0898,0.10973],"tcp_start":[0.50742,-0.05482,0.0288],"tcp_to_object_dist_end":0.19368,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1c6409cc6d884b90ecc3937d36e5ea87cc4ef513b6f301a9da66b4e84390f805`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74667,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.04475,"push_1.push_depth":0.09798,"retract_1.retract_height":0.13271},"optimized_scores":{"best_composite_score":0.67669,"best_fitness_score":0.88669,"best_task_score":0.96651},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":999.0,"contact_point_centroid":[0.51014,-0.10797,-0.00013],"force_p95":66.66908,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":80.69716,"mean_force":23.55984,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49795,-0.05455,0.0199]},{"body_a":"attachment","body_b":"push_box","contact_count":705.0,"contact_point_centroid":[0.51177,-0.06185,0.04365],"force_p95":50.86394,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.56962,"mean_force":21.54518,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49806,-0.05059,0.0199]},{"body_a":"push_box","body_b":"link7","contact_count":498.0,"contact_point_centroid":[0.52482,-0.05421,0.05253],"force_p95":47.62555,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.15432,"mean_force":29.9785,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49875,-0.03334,0.02006]},{"body_a":"push_box","body_b":"link7","contact_count":18.0,"contact_point_centroid":[0.52495,-0.13718,0.05003],"force_p95":8.72864,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.72856,"mean_force":3.77093,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49372,-0.1116,0.0203]},{"body_a":"world","body_b":"push_box","contact_count":3898.0,"contact_point_centroid":[0.50033,-0.15399,-1e-05],"force_p95":0.24594,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.29285,"mean_force":0.27132,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4932,-0.03893,0.05327]},{"body_a":"attachment","body_b":"push_box","contact_count":118.0,"contact_point_centroid":[0.50647,0.00218,0.03495],"force_p95":9.24221,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.12908,"mean_force":3.55967,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49972,0.01405,0.02136]},{"body_a":"world","body_b":"push_box","contact_count":2607.0,"contact_point_centroid":[0.50459,-0.02031,-1e-05],"force_p95":1.70232,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.6298,"mean_force":0.41139,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49817,0.03736,0.02533]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.49591,-0.12961,0.01971],"force_p95":4.67752,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.06976,"mean_force":2.32517,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49577,-0.11764,0.01974]},{"body_a":"world","body_b":"push_box","contact_count":3580.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4992,0.04658,0.17199]}],"total_contact_groups":9},"final_pose_error":0.13208,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50028,-0.15439,0.02499],"final_tcp_position":[0.49446,0.03326,0.08846],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":80.69716,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":895.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3580.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50029,0.06252,0.03384],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":718.0,"n_steps_budget":810.0,"object_pos_end":[0.50593,-0.02715,0.02501],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.123,"object_to_goal_dist_start":0.13127,"object_z_max":0.0251,"peak_contact_force":6.19355,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2725.0,"raw_peak_contact_force":11.12908,"tcp_end":[0.5001,0.00964,0.02069],"tcp_start":[0.50029,0.06252,0.03384],"tcp_to_object_dist_end":0.0375,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":750.0,"n_steps_budget":840.0,"object_pos_end":[0.50034,-0.15447,0.02491],"object_pos_start":[0.50593,-0.02715,0.02501],"object_to_goal_dist_end":0.00449,"object_to_goal_dist_start":0.123,"object_z_max":0.02873,"peak_contact_force":9.68733,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2202.0,"raw_peak_contact_force":80.69716,"tcp_end":[0.4958,-0.11756,0.01976],"tcp_start":[0.5001,0.00964,0.02069],"tcp_to_object_dist_end":0.03754,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50028,-0.15439,0.02499],"object_pos_start":[0.50034,-0.15447,0.02491],"object_to_goal_dist_end":0.0044,"object_to_goal_dist_start":0.00449,"object_z_max":0.02606,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3919.0,"raw_peak_contact_force":16.72856,"tcp_end":[0.49446,0.03326,0.08846],"tcp_start":[0.4958,-0.11756,0.01976],"tcp_to_object_dist_end":0.19818,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f52ec1899e2888770a8b6b3ae605718303ef4b10e72cfd7d20ce53303721b2b0`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73885,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.03885,"push_1.push_depth":0.09867,"retract_1.retract_height":0.15306},"optimized_scores":{"best_composite_score":0.37704,"best_fitness_score":0.58704,"best_task_score":0.67437},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1316.0,"contact_point_centroid":[0.52209,-0.04007,-0.00015],"force_p95":60.17777,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":72.14087,"mean_force":33.01151,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50478,0.01383,0.02148]},{"body_a":"push_box","body_b":"link7","contact_count":768.0,"contact_point_centroid":[0.53164,-0.00605,0.05385],"force_p95":55.61827,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.37127,"mean_force":40.0847,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50463,0.01292,0.02144]},{"body_a":"attachment","body_b":"push_box","contact_count":773.0,"contact_point_centroid":[0.52169,0.00295,0.04894],"force_p95":57.81217,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.9477,"mean_force":37.19233,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50467,0.01332,0.02143]},{"body_a":"push_box","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.52354,-0.07336,0.05477],"force_p95":21.13506,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.53807,"mean_force":10.47144,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49842,-0.05043,0.02199]},{"body_a":"attachment","body_b":"push_box","contact_count":33.0,"contact_point_centroid":[0.51595,-0.05839,0.05163],"force_p95":13.42102,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.34449,"mean_force":2.40689,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49742,-0.04758,0.02267]},{"body_a":"attachment","body_b":"push_box","contact_count":155.0,"contact_point_centroid":[0.51511,0.06822,0.0327],"force_p95":8.92404,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.13218,"mean_force":3.46709,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51,0.08009,0.02163]},{"body_a":"world","body_b":"push_box","contact_count":3890.0,"contact_point_centroid":[0.50107,-0.08593,-2e-05],"force_p95":0.24541,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.06705,"mean_force":0.26401,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49543,0.02281,0.06423]},{"body_a":"world","body_b":"push_box","contact_count":2756.0,"contact_point_centroid":[0.51531,0.04593,-1e-05],"force_p95":2.10612,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.66123,"mean_force":0.44327,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50829,0.1011,0.02653]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50358,0.07681,0.17794]}],"total_contact_groups":9},"final_pose_error":0.07357,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50094,-0.08546,0.02499],"final_tcp_position":[0.4961,0.09024,0.10727],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":72.14087,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51015,0.12542,0.03668],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":765.0,"n_steps_budget":870.0,"object_pos_end":[0.51716,0.0384,0.02502],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.18918,"object_to_goal_dist_start":0.19823,"object_z_max":0.02509,"peak_contact_force":1.58848,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2911.0,"raw_peak_contact_force":10.13218,"tcp_end":[0.51046,0.07523,0.02056],"tcp_start":[0.51015,0.12542,0.03668],"tcp_to_object_dist_end":0.03771,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":777.0,"n_steps_budget":870.0,"object_pos_end":[0.50318,-0.08877,0.02834],"object_pos_start":[0.51716,0.0384,0.02502],"object_to_goal_dist_end":0.06141,"object_to_goal_dist_start":0.18918,"object_z_max":0.02908,"peak_contact_force":27.00761,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2857.0,"raw_peak_contact_force":72.14087,"tcp_end":[0.49872,-0.05052,0.02199],"tcp_start":[0.51046,0.07523,0.02056],"tcp_to_object_dist_end":0.03902,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50094,-0.08546,0.02499],"object_pos_start":[0.50318,-0.08877,0.02834],"object_to_goal_dist_end":0.06455,"object_to_goal_dist_start":0.06141,"object_z_max":0.02844,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3933.0,"raw_peak_contact_force":23.53807,"tcp_end":[0.4961,0.09024,0.10727],"tcp_start":[0.49872,-0.05052,0.02199],"tcp_to_object_dist_end":0.19407,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```