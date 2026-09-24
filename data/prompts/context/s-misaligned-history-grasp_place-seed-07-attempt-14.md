## Search State

- **Seed**: 7
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | pose_tolerance | 11  | 0.3126 | 0.96 | ❌ rejected |
| 13 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10  | 0.3363 | 1.00 | ✅ accepted |
| 12 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10  | 0.2857 | 0.90 | ❌ rejected |
| 11 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10  | 0.3350 | 1.00 | ✅ accepted |
| 10 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10  | -0.0777 | 0.27 | ❌ rejected |

**Proposal policy**: task_score is 0.27 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: grasp_place
- Frozen realised-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`
- Frozen object start: [0.5125095466604667, 0.039721380096957554, 0.03]
- Frozen task target: [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]
- Goal object position: (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5125095466604667, 0.039721380096957554, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5125, 0.0397, 0.03]
  frozen_task_target: [0.6276, 0.1725, 0.145]
  frozen_object_starts: {'grasp_target': [0.5125095466604667, 0.039721380096957554, 0.03]}
  frozen_targets: {'place_target': [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5125095466604667, 0.039721380096957554, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6275685690245193, 0.17252071899905919, 0.14502494273668382) | final destination targets |
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

## Current Skill (Q=-0.078) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_approach
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: reach_grasp_height
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.2
- id: lift_clearance
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: transport_above
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.1
- id: reach_goal
  offset:
  - 0.0
  - 0.0
  - 0.01
  weight: 0.3
phases:
- id: descend_approach
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.06
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_approach
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_height:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_grasp_height
- id: grasp_object
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
  guards:
  - id: grasp_closed
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.01
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: reach_grasp_height
- id: lift_object
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.025
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_clearance
- id: transport_to_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.1
    orientation:
      mode: keep_current
  parameters:
    transport_height:
      type: scalar
      range:
      - 0.04
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_above
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.01
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    place_height_offset:
      type: scalar
      range:
      - 0.0
      - 0.04
      default: 0.01
      binds_to:
      - path: target.offset.z
        mode: replace
    place_speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.015
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **descend_approach** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_height: status=consumed; consumers=target.offset.z (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - parameter_bindings: none
  - guards:
    - id=grasp_closed, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.01
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.025
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.1], tolerance=0.1
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.01], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_height_offset: status=consumed; consumers=target.offset.z (replace)
    - place_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.078
- **task_score** (E): 0.271
- **fitness_score**: 0.592  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.670

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_approach | 1.00 | 1.00 | 0.1476 |
| descend_to_grasp | 1.00 | 1.00 | 0.0983 |
| grasp_object | 1.00 | 1.00 | 0.0123 |
| lift_object | 1.00 | 1.00 | 0.1068 |
| transport_to_goal | 1.00 | 1.00 | 0.0580 |
| descend_to_place | 1.00 | 1.00 | 0.1555 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_approach | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.019, 0.158) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 8.529 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.019, 0.158)→(0.506, 0.022, 0.060) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 27.129 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.506, 0.022, 0.060)→(0.498, 0.021, 0.051) | (0.511, 0.022, 0.026)→(0.511, 0.021, 0.025) | 0.273→0.274 | 1.00 / 36.333 | 0.163 | 0.213 |
| lift_object | lift | 1.00 / step_budget | (0.498, 0.021, 0.051)→(0.505, 0.021, 0.157) | (0.511, 0.021, 0.025)→(0.513, 0.022, 0.129) | 0.274→0.224 | 1.00 / 30.000 | 0.116 | 0.302 |
| transport_to_goal | approach | 1.00 / time_limit | (0.505, 0.021, 0.157)→(0.527, 0.064, 0.187) | (0.513, 0.022, 0.129)→(0.524, 0.069, 0.104) | 0.224→0.203 | 1.00 / 17.000 | 0.111 | 0.632 |
| descend_to_place | descend | 1.00 / step_budget | (0.527, 0.064, 0.187)→(0.596, 0.197, 0.205) | (0.524, 0.069, 0.104)→(0.556, 0.131, 0.016) | 0.203→0.207 | 1.00 / 7.000 | 91004.560 | 0.981 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.418
- phase_score: 0.578
- phase_breakdown.reach_grasp_height_score: 0.720
- phase_breakdown.lift_clearance_score: 0.458
- phase_breakdown.reach_goal_score: 0.680
- phase_breakdown.transport_above_score: 0.069
- phase_breakdown.reach_approach_score: 0.658
- grasp_place_fitness: 0.665

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.665
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.418
- **Median Q (composite search score)**: -0.094
- **K-run variance**: 0.0029
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.354


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `0b279c554151a1bc107b4895d67067efa2444eadb5a644f2482f57ab9ff93d7f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `079d4532bc3cff86c1b89933c7940f2ee474dc4233e12f8d134c76ceb3cd8d4d`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.46212,"average_solve_count":396.0,"average_success_count":396.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_approach.approach_height":0.1014,"descend_approach.approach_speed":0.09288,"descend_to_grasp.descend_speed":0.01445,"descend_to_grasp.grasp_height":0.02002,"descend_to_place.place_height_offset":0.01812,"descend_to_place.place_speed":0.00512,"lift_object.lift_height":0.1404,"lift_object.lift_speed":0.024,"transport_to_goal.transport_duration":4.45353,"transport_to_goal.transport_height":0.14457,"transport_to_goal.transport_speed":0.09583},"optimized_scores":{"best_composite_score":-0.00458,"best_fitness_score":0.66542,"best_task_score":0.41782},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":228.0,"contact_point_centroid":[0.61069,0.1697,-0.00605],"force_p95":0.87334,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.22105,"mean_force":0.29308,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60703,0.15337,0.15994]},{"body_a":"world","body_b":"grasp_target","contact_count":110.0,"contact_point_centroid":[0.50998,0.03756,-0.00181],"force_p95":0.27376,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29224,"mean_force":0.12824,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49816,0.03755,0.05147]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3561.0,"contact_point_centroid":[0.50143,0.01841,0.08671],"force_p95":0.12089,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26245,"mean_force":0.07921,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50072,0.03753,0.08826]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1639.0,"contact_point_centroid":[0.56908,0.08766,0.17058],"force_p95":0.16118,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24268,"mean_force":0.11184,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56341,0.10583,0.17568]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5553.0,"contact_point_centroid":[0.5007,0.0561,0.09247],"force_p95":0.08881,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23283,"mean_force":0.05287,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50117,0.03755,0.09242]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.03962,-0.00218],"force_p95":0.17537,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22361,"mean_force":0.13565,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50033,0.03774,0.05196]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9980.0,"contact_point_centroid":[0.52685,0.04244,0.15825],"force_p95":0.11464,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20769,"mean_force":0.09168,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5241,0.06087,0.16156]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11484.0,"contact_point_centroid":[0.52395,0.077,0.15662],"force_p95":0.11831,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19544,"mean_force":0.08118,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52217,0.05862,0.15929]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1772.0,"contact_point_centroid":[0.57017,0.1251,0.17005],"force_p95":0.12377,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16792,"mean_force":0.10072,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56464,0.10718,0.17521]},{"body_a":"world","body_b":"grasp_target","contact_count":1188.0,"contact_point_centroid":[0.51251,0.03972,-0.00189],"force_p95":0.13631,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"descend_approach","phase_type":"descend","tcp_position_centroid":[0.5031,0.01631,0.22601]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3389.0,"contact_point_centroid":[0.50181,0.0185,0.05013],"force_p95":0.10919,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13154,"mean_force":0.06339,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49919,0.03765,0.05069]},{"body_a":"world","body_b":"grasp_target","contact_count":964.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50616,0.0359,0.10587]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4864.0,"contact_point_centroid":[0.49996,0.05643,0.05095],"force_p95":0.07502,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07858,"mean_force":0.04395,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4992,0.03765,0.0507]}],"total_contact_groups":13},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61079,0.16993,0.01523],"final_tcp_position":[0.6132,0.15995,0.15797],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1188.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_approach","tcp_end":[0.50764,0.0339,0.14947],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12369,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":241.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":964.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp_height","tcp_end":[0.50728,0.03828,0.05994],"tcp_start":[0.50764,0.0339,0.14947],"tcp_to_object_dist_end":0.03435,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51248,0.03812,0.02528],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21365,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.17552,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10053.0,"raw_peak_contact_force":0.22361,"subtask_id":"reach_grasp_height","tcp_end":[0.49916,0.03764,0.05066],"tcp_start":[0.50728,0.03828,0.05994],"tcp_to_object_dist_end":0.02867,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.51533,0.03867,0.11383],"object_pos_start":[0.51248,0.03812,0.02528],"object_to_goal_dist_end":0.17744,"object_to_goal_dist_start":0.21365,"object_z_max":0.11347,"peak_contact_force":0.12272,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9224.0,"raw_peak_contact_force":0.29224,"subtask_id":"lift_clearance","tcp_end":[0.50671,0.03773,0.14144],"tcp_start":[0.49916,0.03764,0.05066],"tcp_to_object_dist_end":0.02895,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55046,0.08465,0.14957],"object_pos_start":[0.51533,0.03867,0.11383],"object_to_goal_dist_end":0.117,"object_to_goal_dist_start":0.17744,"object_z_max":0.14954,"peak_contact_force":0.11437,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21464.0,"raw_peak_contact_force":0.20769,"subtask_id":"transport_above","tcp_end":[0.54533,0.08444,0.18674],"tcp_start":[0.50671,0.03773,0.14144],"tcp_to_object_dist_end":0.03752,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":332.0,"n_steps_budget":1000.0,"object_pos_end":[0.61079,0.16993,0.01523],"object_pos_start":[0.55046,0.08465,0.14957],"object_to_goal_dist_end":0.1309,"object_to_goal_dist_start":0.117,"object_z_max":0.14957,"peak_contact_force":0.08843,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3639.0,"raw_peak_contact_force":1.22105,"subtask_id":"reach_goal","tcp_end":[0.6132,0.15995,0.15797],"tcp_start":[0.54533,0.08444,0.18674],"tcp_to_object_dist_end":0.14311,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a74f7c08b88460953bfa7e35b953cddf9278fdc17d2d4db8a2ea121b328e8b73`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96389,"average_solve_count":360.0,"average_success_count":360.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_approach.approach_height":0.0983,"descend_approach.approach_speed":0.05793,"descend_to_grasp.descend_speed":0.03231,"descend_to_grasp.grasp_height":0.02033,"descend_to_place.place_height_offset":0.01266,"descend_to_place.place_speed":0.01675,"lift_object.lift_height":0.17274,"lift_object.lift_speed":0.03233,"transport_to_goal.transport_duration":3.52056,"transport_to_goal.transport_height":0.09339,"transport_to_goal.transport_speed":0.05048},"optimized_scores":{"best_composite_score":-0.13436,"best_fitness_score":0.53564,"best_task_score":0.15993},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":830.0,"contact_point_centroid":[0.47611,0.09277,-0.00319],"force_p95":0.59899,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.55353,"mean_force":0.17353,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49071,0.07476,0.19183]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.47971,0.04625,-0.00174],"force_p95":0.28555,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30107,"mean_force":0.13274,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46977,0.04618,0.05291]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3717.0,"contact_point_centroid":[0.47196,0.02744,0.1062],"force_p95":0.12234,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27853,"mean_force":0.08739,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47256,0.04625,0.10848]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4810.0,"contact_point_centroid":[0.4727,0.06473,0.10317],"force_p95":0.1109,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26705,"mean_force":0.07224,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47226,0.04623,0.10471]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7786.0,"contact_point_centroid":[0.47864,0.03979,0.17646],"force_p95":0.12156,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25063,"mean_force":0.08412,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.4816,0.05858,0.17903]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48276,0.04855,-0.00219],"force_p95":0.17892,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23049,"mean_force":0.13666,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47179,0.04639,0.05311]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9429.0,"contact_point_centroid":[0.48065,0.07739,0.17566],"force_p95":0.09479,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1801,"mean_force":0.07052,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48181,0.05899,0.17933]},{"body_a":"world","body_b":"grasp_target","contact_count":1268.0,"contact_point_centroid":[0.4827,0.04873,-0.00189],"force_p95":0.13591,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"descend_approach","phase_type":"descend","tcp_position_centroid":[0.4906,0.01999,0.22493]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2420.0,"contact_point_centroid":[0.4717,0.02736,0.04962],"force_p95":0.10874,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13237,"mean_force":0.08311,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47071,0.04628,0.05198]},{"body_a":"world","body_b":"grasp_target","contact_count":896.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47911,0.04418,0.10411]},{"body_a":"world","body_b":"grasp_target","contact_count":2204.0,"contact_point_centroid":[0.4761,0.09314,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.53157,0.14762,0.21115]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4366.0,"contact_point_centroid":[0.47143,0.065,0.0513],"force_p95":0.08885,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0953,"mean_force":0.05055,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47072,0.04628,0.05199]},{"body_a":"left_finger","body_b":"right_finger","contact_count":591.0,"contact_point_centroid":[0.49158,0.07571,0.19477],"force_p95":0.01347,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01656,"mean_force":0.01122,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49126,0.0757,0.1926]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2373.0,"contact_point_centroid":[0.53225,0.14805,0.21348],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01268,"mean_force":0.01036,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5318,0.14802,0.21126]}],"total_contact_groups":14},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.4761,0.09314,0.01602],"final_tcp_position":[0.57217,0.21596,0.23155],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":25.34193,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":318.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":25.34193,"phase_name":"descend_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1268.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_approach","tcp_end":[0.48189,0.04168,0.14685],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12104,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":224.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":896.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp_height","tcp_end":[0.47847,0.047,0.06028],"tcp_start":[0.48189,0.04168,0.14685],"tcp_to_object_dist_end":0.03456,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48267,0.04701,0.02525],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2916,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.17216,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8586.0,"raw_peak_contact_force":0.23049,"subtask_id":"reach_grasp_height","tcp_end":[0.47068,0.04628,0.05195],"tcp_start":[0.47847,0.047,0.06028],"tcp_to_object_dist_end":0.02928,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":323.0,"n_steps_budget":1000.0,"object_pos_end":[0.48329,0.04715,0.14388],"object_pos_start":[0.48267,0.04701,0.02525],"object_to_goal_dist_end":0.22413,"object_to_goal_dist_start":0.2916,"object_z_max":0.14351,"peak_contact_force":0.1176,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8619.0,"raw_peak_contact_force":0.30107,"subtask_id":"lift_clearance","tcp_end":[0.47793,0.04657,0.1737],"tcp_start":[0.47068,0.04628,0.05195],"tcp_to_object_dist_end":0.03031,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4761,0.09314,0.01602],"object_pos_start":[0.48329,0.04715,0.14388],"object_to_goal_dist_end":0.27496,"object_to_goal_dist_start":0.22413,"object_z_max":0.15113,"peak_contact_force":0.12262,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18636.0,"raw_peak_contact_force":1.55353,"subtask_id":"transport_above","tcp_end":[0.49253,0.07789,0.19437],"tcp_start":[0.47793,0.04657,0.1737],"tcp_to_object_dist_end":0.17976,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":551.0,"n_steps_budget":1000.0,"object_pos_end":[0.4761,0.09314,0.01602],"object_pos_start":[0.4761,0.09314,0.01602],"object_to_goal_dist_end":0.27496,"object_to_goal_dist_start":0.27496,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4577.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.57217,0.21596,0.23155],"tcp_start":[0.49253,0.07789,0.19437],"tcp_to_object_dist_end":0.26602,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b1a72366a9c9a56aa2e80fc4399e157c8281abf492ab3c1ede02058762a86ed7`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.94278,"average_solve_count":367.0,"average_success_count":367.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_approach.approach_height":0.13119,"descend_approach.approach_speed":0.06222,"descend_to_grasp.descend_speed":0.02754,"descend_to_grasp.grasp_height":0.02024,"descend_to_place.place_height_offset":0.02912,"descend_to_place.place_speed":0.01974,"lift_object.lift_height":0.15483,"lift_object.lift_speed":0.03258,"transport_to_goal.transport_duration":2.94087,"transport_to_goal.transport_height":0.09804,"transport_to_goal.transport_speed":0.07318},"optimized_scores":{"best_composite_score":-0.09408,"best_fitness_score":0.57592,"best_task_score":0.23641},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1081.0,"contact_point_centroid":[0.58177,0.13093,-0.00297],"force_p95":0.50403,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.59957,"mean_force":0.16166,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59077,0.1778,0.21464]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3279.0,"contact_point_centroid":[0.55519,0.09008,0.18248],"force_p95":0.14404,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39312,"mean_force":0.08875,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.555,0.07144,0.18686]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.53434,-0.02068,-0.0016],"force_p95":0.29563,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31183,"mean_force":0.14637,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5218,-0.02053,0.05031]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6218.0,"contact_point_centroid":[0.52541,-0.03962,0.10068],"force_p95":0.08277,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22865,"mean_force":0.05422,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52527,-0.02057,0.10006]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5565.0,"contact_point_centroid":[0.52567,-0.00142,0.10156],"force_p95":0.09459,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22563,"mean_force":0.06142,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52536,-0.02058,0.10089]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53705,-0.02127,-0.00207],"force_p95":0.14263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18477,"mean_force":0.12792,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52394,-0.02057,0.05104]},{"body_a":"world","body_b":"grasp_target","contact_count":1028.0,"contact_point_centroid":[0.53702,-0.02132,-0.00187],"force_p95":0.13676,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1231,"phase_index":0.0,"phase_name":"descend_approach","phase_type":"descend","tcp_position_centroid":[0.51266,-0.00846,0.24042]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11765.0,"contact_point_centroid":[0.53629,0.02279,0.1633],"force_p95":0.10862,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13406,"mean_force":0.0786,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53563,0.00403,0.16559]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14426.0,"contact_point_centroid":[0.53536,-0.01535,0.16304],"force_p95":0.09605,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12413,"mean_force":0.06578,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53533,0.00317,0.16505]},{"body_a":"world","body_b":"grasp_target","contact_count":1208.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.5281,-0.01915,0.11927]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4351.0,"contact_point_centroid":[0.52369,-0.00136,0.05025],"force_p95":0.07333,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11642,"mean_force":0.04951,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52276,-0.02055,0.04965]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3868.0,"contact_point_centroid":[0.55657,0.05683,0.18347],"force_p95":0.09707,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11372,"mean_force":0.0712,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55619,0.07517,0.18773]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4913.0,"contact_point_centroid":[0.5236,-0.03969,0.05018],"force_p95":0.06982,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07946,"mean_force":0.04448,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52276,-0.02055,0.04965]},{"body_a":"left_finger","body_b":"right_finger","contact_count":912.0,"contact_point_centroid":[0.59391,0.18567,0.21903],"force_p95":0.01286,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01646,"mean_force":0.01067,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59347,0.18566,0.21676]}],"total_contact_groups":14},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.58179,0.13105,0.01602],"final_tcp_position":[0.60313,0.21378,0.2243],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273013.46851,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":258.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"descend_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_approach","tcp_end":[0.52774,-0.01771,0.17817],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15248,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":302.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1208.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp_height","tcp_end":[0.53116,-0.02069,0.05975],"tcp_start":[0.52774,-0.01771,0.17817],"tcp_to_object_dist_end":0.03424,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53696,-0.02078,0.02574],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31647,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14128,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11064.0,"raw_peak_contact_force":0.18477,"subtask_id":"reach_grasp_height","tcp_end":[0.52273,-0.02055,0.04961],"tcp_start":[0.53116,-0.02069,0.05975],"tcp_to_object_dist_end":0.02779,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":304.0,"n_steps_budget":1000.0,"object_pos_end":[0.54096,-0.02096,0.13028],"object_pos_start":[0.53696,-0.02078,0.02574],"object_to_goal_dist_end":0.26947,"object_to_goal_dist_start":0.31647,"object_z_max":0.12994,"peak_contact_force":0.10821,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11875.0,"raw_peak_contact_force":0.31183,"subtask_id":"lift_clearance","tcp_end":[0.53141,-0.02067,0.15654],"tcp_start":[0.52273,-0.02055,0.04961],"tcp_to_object_dist_end":0.02795,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54471,0.03016,0.14593],"object_pos_start":[0.54096,-0.02096,0.13028],"object_to_goal_dist_end":0.21709,"object_to_goal_dist_start":0.26947,"object_z_max":0.14591,"peak_contact_force":0.09569,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26191.0,"raw_peak_contact_force":0.13406,"subtask_id":"transport_above","tcp_end":[0.5439,0.03056,0.18084],"tcp_start":[0.53141,-0.02067,0.15654],"tcp_to_object_dist_end":0.03492,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":662.0,"n_steps_budget":1000.0,"object_pos_end":[0.58179,0.13105,0.01602],"object_pos_start":[0.54471,0.03016,0.14593],"object_to_goal_dist_end":0.21633,"object_to_goal_dist_start":0.21709,"object_z_max":0.15936,"peak_contact_force":273013.46851,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9140.0,"raw_peak_contact_force":1.59957,"subtask_id":"reach_goal","tcp_end":[0.60313,0.21378,0.2243],"tcp_start":[0.5439,0.03056,0.18084],"tcp_to_object_dist_end":0.22513,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```